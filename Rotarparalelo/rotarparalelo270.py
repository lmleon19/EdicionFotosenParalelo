
from mpi4py import MPI
import numpy as np
import ImageFilter
from numpy import array, shape, reshape, zeros, transpose
from PIL import Image, ImageChops, ImageOps
import StringIO
import time

comm = MPI.COMM_WORLD  # comunicador entre dos procesadores #
rank = comm.rank     # id procesador actual #
size = comm.size     # tamano procesador #

def convertirImgMatrixRGB(img):
	return np.array(img.convert("RGB"))

def rotar90(img):
    #arrImg = convertirImgMatrixRGB(img)
    n = len(img[0])
    m = len(img)
    final = np.array(Image.new("RGB",(m,n)))
    for i in range(n): #fila
        for j in range(m): #columna
            final[i][j] = img[::, ((i*-1)-1)][j]
    return final

def rotar180(img):
    return rotar90(rotar90(img)) #debido a que el algoritmo de cambio de posicion es el mismo

def rotar270(img):
    return rotar180(rotar90(img))

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

def main():
    starting_point=time.time()
    
    if rank == 0:
        ruta="1.jpg"
        divisionTareaImagen(ruta)

    if rank != 0:
        arrTrabajo = comm.recv(source = 0)    #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        arrImgSalida = rotar270(arrTrabajo)    #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen
        comm.send(arrImgSalida,dest=0)

    if rank == 0:       #recibe los arreglos y los junta uno abajo del otro
        for i in range(1, size):
            if i > 1:
                construcImg = np.concatenate((comm.recv(source = i),construcImg), axis=1)
            if i == 1:
                construcImg = comm.recv(source = i)
        imgContrucFinal = Image.fromarray(construcImg)
        imgContrucFinal.save("imagentranspuesta270.png")
        
    elapsed_time=time.time()-starting_point
    print ""
    print "Tiempo paralelo [s]: " + str(elapsed_time)

main()
