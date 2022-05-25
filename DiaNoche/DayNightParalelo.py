# coding=utf-8

import numpy as np
from PIL import ImageEnhance
import numpy as np
from StringIO import StringIO
import time
from mpi4py import MPI
from PIL import Image,ImageChops
import StringIO

starting_point=time.time()

comm = MPI.COMM_WORLD  # comunicador entre dos procesadores
rank = comm.rank     # id procesador actual
size = comm.size     # cantidad de procesadores a usar

# convierte una imagen tipo Imagen (de la libreria PIL) en una matriz(ETD) con la informacion RGB de la imagen
def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))

def PasarDiaNoche(arrImg):
    #img=img.convert('L') #desaturar la imagen
    #arrImg = convertirImgMatrixRGB(img)
    for i in range(len(arrImg)):
        for j in range(len(arrImg[0])):
            arrImg[i][j][0] = arrImg[i][j][0] * 0.2 #rojo
            arrImg[i][j][1] = arrImg[i][j][0] * 1.2 #verde
            arrImg[i][j][2] = arrImg[i][j][0] * 3.5 #azul
    imgNoche = Image.fromarray(arrImg)
    contraste = ImageEnhance.Contrast(imgNoche)
    imgNoche = contraste.enhance(1.2) #asigna un valor para el contraste de la imagen
    brillo = ImageEnhance.Brightness(imgNoche)
    imgNoche = brillo.enhance(0.7) #asigna un valor para el brillo de la imagen
    nitidez = ImageEnhance.Sharpness(imgNoche)
    imgNoche = nitidez.enhance(2) #asigna un valor para la nitidez de la imagen
    arrImg=convertirImgMatrixRGB(imgNoche)

    return arrImg

def divisionTareaImagen(ruta):
    img=Image.open(ruta)
    imgSize=img.size
    largo=imgSize[1]
    ancho=imgSize[0]
    tamanoParte=largo/(size-1)  #(size-1) es para no incluir el procesador cero
    xInicio=0
    yInicio=0
    tamPar=tamanoParte
    for i in range(1,size):
        parteImgEnvio=img.crop((xInicio,yInicio,ancho,tamPar))
        tamPar=tamPar+tamanoParte
        yInicio=yInicio+tamanoParte
        rutaSalida="photoCut"+str(i)+".png"
        parteImgEnvio.save(rutaSalida)
        arrImg=convertirImgMatrixRGB(parteImgEnvio)
        comm.send(arrImg,dest=i)

def main():
    starting_point=time.time()

    if rank==0:
        ruta="paisaje2.jpg"
        divisionTareaImagen(ruta)
    if rank!=0:
        arrTrabajo=comm.recv(source=0)    #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        arrImgSalida=PasarDiaNoche(arrTrabajo)    #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen
        comm.send(arrImgSalida,dest=0)
    if rank==0 :       #recibe los arreglos y los junta uno abajo del otro
        for i in range(1,size):
            if i > 1:
                construcImg = np.concatenate((construcImg,comm.recv(source=i)))
            if i == 1:
                construcImg = comm.recv(source=i)
        imgContrucFinal=Image.fromarray(construcImg)
        imgContrucFinal.save("IMAGENFINAL.png")

    elapsed_time=time.time()-starting_point
    print ""
    print "Tiempo paralelo [s]: " + str(elapsed_time)


main()
