from __future__ import division


import numpy as np
from PIL import Image
from PIL import ImageEnhance
import time #Libreria

# convierte una imagen tipo Imagen (de la libreria PIL) en una matriz(ETD) con la informacion RGB de la imagen
def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))


#Trabajando en como matriz siempre
def aplicarBrillo(img,factor):
    arrImg=convertirImgMatrixRGB(img)
    #si el factor es menor a cero la imagen se oscurece (rango 0 a -1)
    if factor <0:#para oscurecer la imagen
        for i in range(img.size[1]):
            for j in range(img.size[0]):
                brillo= lambda x: x*(1+factor)
                arrImg[i][j]=brillo(arrImg[i][j])
    #si el factor es mayor a cero se aclara (rango 0 a 1)
    else:#brillo
        for i in range(img.size[1]):
            for j in range(img.size[0]):
                brillo= lambda x: x+ (255-x)*factor
                arrImg[i][j]=brillo(arrImg[i][j])
    imgBrillante=Image.fromarray(arrImg)#se devuelve la matriz a imagen
    return imgBrillante

def main():


    #aplicar brillo
    print"Ingrese factor(se debe ingresar valor decimal entre -1 y 0 para oscurecer y entre 0 y 1 para aclarar)"


    factor=input()
    img=Image.open("1.jpg")
    starting_point=time.time() #Donde quiere empezar a calcular el tiempo
    imgBrillo = aplicarBrillo(img,factor)
    imgBrillo.save("resultado1.jpg")
    elapsed_time=time.time()-starting_point #calculo
    print ""
    print "Serial Time [seconds]: " + str(elapsed_time) #segundos
    imgBrillo.show()


import time #Libreria
main() #donde realiza las acciones para el brillo
