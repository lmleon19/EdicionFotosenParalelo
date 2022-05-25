
from mpi4py import MPI
import numpy as np
import ImageFilter
from numpy import array, shape, reshape, zeros, transpose
from PIL import Image, ImageChops, ImageOps
import StringIO
import time
import math

comm = MPI.COMM_WORLD  # comunicador entre dos procesadores #
rank = comm.rank     # id procesador actual #
size = comm.size     # tamano procesador #

def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))


def convolucion(imagen_original, mascara):
    x, y = imagen_original.size
    pos = imagen_original.load()
    nueva_imagen = Image.new("RGB", (x,y))
    pos_nueva = nueva_imagen.load()
    for i in range(x):
        for j in range(y):
            total = 0
            for n in range(i-1, i+2):
                for m in range(j-1, j+2):
                    if n >= 0 and m >= 0 and n < x and m < y:
                        total += mascara[n - (i - 1)][ m - (j - 1)] * pos[n, m][0]
            pos_nueva[i, j] = (total, total, total)
    nueva_imagen.save("mascara.png")
    return nueva_imagen


def umbral(imagen_original):
    x, y = imagen_original.size
    imagen_umbral = Image.new("RGB", (x, y))
    pixeles = []
    for a in range(y):
        for b in range(x):
            color = imagen_original.getpixel((b,a))[0]
            if color > 80:
                color = 255
            else:
                color = 0
            data = (color, color, color)
            pixeles.append(data)
    imagen_umbral.putdata(pixeles)
    imagen_umbral.save("imagen_umbral.png", quality=100)
    return imagen_umbral

def hacer_difusa(imagen_original):
    """funcion que se encarga de tomar de cada pixel los pixeles
    de izq, derecha, arriba, abajo y el mismo y los promedia, y ese
    promedio es el valor de los nuevos pixeles
    """
    x, y = imagen_original.size
    imagen_difusa = Image.new("RGB", (x, y))
    pixeles = []
    #temp sirve para obtener el promedio de los
    #pixeles contiguos
    temp = []
    for a in range(y):
        for b in range(x):
            actual = imagen_original.getpixel((b, a))[0]
            if b>0 and b<(x-1) and a>0 and a<(y-1):
                    #en esta condicion entran todos los pixeles que no estan
                    #en el margen de la imagen, es decir casi todos
                pix_izq = imagen_original.getpixel((b-1, a))[0]
                pix_der = imagen_original.getpixel((b+1, a))[0]
                pix_arriba = imagen_original.getpixel((b, a+1))[0]
                pix_abajo = imagen_original.getpixel((b, a-1))[0]
                temp.append(pix_izq)
                temp.append(pix_der)
                temp.append(pix_arriba)
                temp.append(pix_abajo)
            else:
                #aqui entran todos los pixeles de la orilla
                try:
                    pix_abajo = imagen_original.getpixel((b, a-1))[0]
                    temp.append(pix_abajo)
                except:
                    pass
                try:
                    pix_der = imagen_original.getpixel((b+1, a))[0]
                    temp.append(pix_der)
                except:
                    pass
                try:
                    pix_izq = imagen_original.getpixel((b-1, a))[0]
                    temp.append(pix_izq)
                except:
                    pass
                try:
                    pix_arriba = imagen_original.getpixel((b, a+1))[0]
                    temp.append(pix_arriba)
                except:
                    pass
            temp.append(actual)
                #se obtiene el promedio para cambiar el pixel
            prom = sum(temp)/len(temp)
            temp = []
            pixeles.append((prom, prom, prom))
    imagen_difusa.putdata(pixeles)
    imagen_difusa.save("imagen_difusa.png")
    return imagen_difusa

def hacer_gris(imagen):
    img = Image.fromarray(imagen)
    n = img.size[0]
    m = img.size[1]
    for i in range(n):
        for j in range(m):
            # Obtenemos los colores RGB pixel por pixel
            r, g, b = img.getpixel((i, j))
            # Cambiamos el RGB del pixel
            img.putpixel((i, j), ((r+g+b)/3, (r+g+b)/3, (r+g+b)/3))
    return convertirImgMatrixRGB(img)

def divisionTareaImagen(ruta):
    img = Image.open(ruta)
    imgSize = img.size
    largo = imgSize[1]
    ancho = imgSize[0]
    tamanoParte = largo/(size-1)  #(size-1) es para no incluir el procesador cero
    xInicio = 0
    yInicio = 0
    tamPar = tamanoParte
    for i in range(1,size):
        parteImgEnvio = img.crop((xInicio, yInicio, ancho, tamPar))
        tamPar = tamPar+tamanoParte
        yInicio = yInicio+tamanoParte
        rutaSalida = "photoCut" + str(i) + ".png"
        parteImgEnvio.save(rutaSalida)
        arrImg = convertirImgMatrixRGB(parteImgEnvio)
        comm.send(arrImg, dest = i)

def normalizar(imagen_original):
    imagen_original=Image.fromarray(imagen_original)
    x, y = imagen_original.size
    imagen_normalizada = Image.new("RGB", (x, y))
    pixeles = []
    for a in range(y):
        for b in range(x):
            pix = imagen_original.getpixel((b, a))[0]
            pixeles.append(pix)
    maximo = max(pixeles)
    minimo = min(pixeles)
    # print maximo
    # print minimo
    l = 256.0/(maximo - minimo)
    pixeles = []
    for a in range(y):
        for b in range(x):
            pix = imagen_original.getpixel((b, a))[0]
            nuevo_pix = int(math.floor((pix-minimo)*l))
            pixeles.append((nuevo_pix, nuevo_pix, nuevo_pix))
    imagen_normalizada.putdata(pixeles)
    imagen_normalizada.save("normalizada"+str(rank)+".png")
    return convertirImgMatrixRGB(imagen_normalizada)

def main():
    starting_point=time.time()
    
    if rank == 0:
        ruta="03.jpg"
        divisionTareaImagen(ruta)

    if rank != 0:
        arrTrabajo = comm.recv(source = 0)    #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        arrImgSalida = hacer_gris(arrTrabajo)    #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen
        comm.send(arrImgSalida,dest=0)

    if rank == 0:       #recibe los arreglos y los junta uno abajo del otro
        for i in range(1, size):
            if i > 1:
                construcImg = np.concatenate((construcImg, comm.recv(source = i)), axis=0)
            if i == 1:
                construcImg = comm.recv(source = i)
        imgContrucFinal = Image.fromarray(construcImg)
        imgContrucFinal.save("imagen_gris.png")
        #Gris creada


    if rank == 0:
        ruta="imagen_gris.png"
        divisionTareaImagen(ruta)

    if rank != 0:
        arrTrabajo = comm.recv(source = 0)    #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        arrImgSalida = normalizar(arrTrabajo)    #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen
        comm.send(arrImgSalida, dest=0)

    if rank == 0:      #recibe los arreglos y los junta uno abajo del otro
        for i in range(1, size):
            if i > 1:
                construcImg = np.concatenate((construcImg, comm.recv(source = i)), axis=0)
            if i == 1:
                construcImg = comm.recv(source = i)
        # print ""
        # print rank
        # print ""
        nueva = Image.fromarray(construcImg)
        nueva.save("imagen_normalizada.png")

        mascara1 = [[-1,0,1],[-2,0,2],[-1,0,1]]
        mascara2 = [[1,1,1],[0,0,0],[-1,-1,-1]]
        mascara3 = [[1,1,1],[-1,-2,1],[-1,-1,1]]
        mascara4 = [[-1,1,1],[-1,-2,1],[-1,1,1]]
        nueva = convolucion(nueva, mascara1)
        nueva.save("031.png")
        nueva = convolucion(nueva, mascara2)
        nueva.save("032.png")
        nueva = convolucion(nueva, mascara3)
        nueva.save("033.png")
        nueva = convolucion(nueva, mascara4)
        nueva.save("034.png")

        nueva = hacer_difusa(nueva)
        nueva = umbral(nueva)

        elapsed_time=time.time()-starting_point
        print ""
        print "Tiempo paralelo [s]: " + str(elapsed_time)
        print ""

main()