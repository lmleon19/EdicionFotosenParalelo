from __future__ import division


import numpy as np
from PIL import Image
from PIL import ImageEnhance

# convierte una imagen tipo Imagen (de la libreria PIL) en una matriz(ETD) con la informacion RGB de la imagen
def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))


def rotar90(img):
    arrImg = convertirImgMatrixRGB(img)
    n = img.size[0]
    m = img.size[1]
    final = np.array(Image.new("RGB",(m,n)))
    for i in range(n): #fila
        for j in range(m): #columna
            final[i][j] = arrImg[::, ((i*-1)-1)][j]
    imgColor = Image.fromarray(final)
    return imgColor

def rotar180(img):
    return rotar90(rotar90(img)) #debido a que el algoritmo de cambio de posicion es el mism

def aplicarReflejo(img):
    inv = img #se hace una copia de la imagen
    inv = rotar180(inv) #se gira

    copiaInvertida = convertirImgMatrixRGB(inv) #se convierten en matrices ambas imagenes

    imgMatriz = convertirImgMatrixRGB(img)
    filas = img.size[1]
    columnas = img.size[0]

    #Es una idea

    print "MATRIZ ORIGINAL"
    print imgMatriz
    for i in range (0,filas):
        for j in range(0,columnas):
            aux = imgMatriz[i][j]
            copiaInvertida[filas-1][j] = aux
        filas=filas-1
    print "MATRIZ MODIFICADA"
    print copiaInvertida

    arreglo = np.vstack((imgMatriz,copiaInvertida))

    imgInvertida = Image.fromarray(arreglo)
    return imgInvertida

def main():
    img=Image.open("imagenMuestra2.jpg")
    imgReflejo = aplicarReflejo(img)
    imgReflejo.save("reflejo.jpg")

import time #Libreria
starting_point=time.time() #Donde quiere empezar a calcular el tiempo
main()
elapsed_time=time.time()-starting_point #calculo
print ""
print "Serial Time [seconds]: " + str(elapsed_time) #segundos

