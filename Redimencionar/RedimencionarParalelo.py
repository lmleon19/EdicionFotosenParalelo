# -*- coding: cp1252 -*-
__author__ = 'Luis Miguel leon'
from mpi4py import MPI
import numpy as np
from PIL import Image
import time

comm = MPI.COMM_WORLD # comunicador entre dos procesadores #
rank = comm.rank # id procesador actual #
size = comm.size # tamano procesador #

def divisionTareaImagen(ruta):
    img = Image.open(ruta)
    imgSize = img.size
    largo = imgSize[1]
    ancho = imgSize[0]
    tamanoParte = largo/(size-1) #(size-1) es para no incluir el procesador cero
    print tamanoParte
    xInicio = 0
    yInicio = 0
    tamPar = tamanoParte

    REDIMXXX = 1000
    REDIMYYY = 2000
    REDIMYYY = REDIMYYY/(size-1)

    for i in range(1,size):
        parteImgEnvio = img.crop((xInicio, yInicio, ancho, tamPar))
        tamPar = tamPar+tamanoParte
        yInicio = yInicio+tamanoParte
        rutaSalida = "photoCut" + str(i) + ".png"
        parteImgEnvio.save(rutaSalida)

        imag = Image.open("base.png")
        imag = imag.resize((REDIMXXX, REDIMYYY), Image.ANTIALIAS)
        imag.save("output1.png")

        arrImg = convertirImgMatrixRGB(parteImgEnvio)

        comm.send(arrImg, dest = i)

def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))

def redimencionarImg(img,img2):
    ancho=img.size[0]
    alto=img.size[1]
    finalAncho=img2.size[0]
    finAlto= img2.size[1]
    distanX = (ancho-1)/float(finalAncho)
    distanY = (alto-1) /float(finAlto)
    arrImg=convertirImgMatrixRGB(img)
    arrImg2=convertirImgMatrixRGB(img2)

    print "*********************"
#   Proceso de redimensionado
    for i in range(finAlto ):
        for j in range(finalAncho):
            x = (distanX * j);
            y = (distanY * i);

            a = arrImg[y] [x]
            b = arrImg[y+1][x]
            c = arrImg[y][x+1]
            d = arrImg[y+1][x+1]

            diferX = (distanX * j) - x;
            diferY = (distanY * i) - y;

            blue =  ((a[2])&0xff)*(1-diferX)*(1-diferY) + ((b[2])&0xff)*(diferX)*(1-diferY) + ((c[2])&0xff)*(diferY)*(1-diferX) + ((d[2])&0xff)*(diferX*diferY)
            green = ((a[1])&0xff)*(1-diferX)*(1-diferY) + ((b[1])&0xff)*(diferX)*(1-diferY) + ((c[1])&0xff)*(diferY)*(1-diferX) + ((d[1])&0xff)*(diferX*diferY)
            red =   ((a[0])&0xff)*(1-diferX)*(1-diferY) + ((b[0])&0xff)*(diferX)*(1-diferY) + ((c[0])&0xff)*(diferY)*(1-diferX) + ((d[0])&0xff)*(diferX*diferY)

            nuevoPixel = arrImg2[i][j]
            nuevoPixel[0]=red 
            nuevoPixel[1]=green 
            nuevoPixel[2]=blue

            arrImg2[i][j] = nuevoPixel;
    
    #imgRedimencionada=Image.fromarray(arrImg2)
    return arrImg2

def main():
    if rank==0:
        divisionTareaImagen("tatuajr.png")
        starting_point=time.time()
    
    if rank!=0:
        arrTrabajo = comm.recv(source = 0) #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        img1=Image.fromarray(arrTrabajo)
        img2=Image.open("output1.png")
        arrImgSalida = redimencionarImg(img1, img2) #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen

        #img8=Image.fromarray(arrImgSalida)
        #img8.save("qqqqq"+str(rank)+".png")

        comm.send(arrImgSalida,dest=0)

    if rank == 0: #recibe los arreglos y los junta uno abajo del otro
        for i in range(1, size):
            if i > 1:
                construcImg = np.concatenate((construcImg, comm.recv(source = i)), axis=0)
            if i == 1:
                construcImg = comm.recv(source = i)
        imgContrucFinal = Image.fromarray(construcImg)
        imgContrucFinal.save("FINALFINAL.png")
        elapsed_time=time.time()-starting_point
        print "Tiempo Paralelo [segundos]: " + str(elapsed_time)
    print "fin" + str(rank)

main()





