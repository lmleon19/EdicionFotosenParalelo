
import ImageFilter
import numpy as np
import time
from numpy import array, shape, reshape, zeros, transpose
from PIL import Image, ImageChops, ImageOps


# convierte una imagen tipo Imagen (de la libreria PIL) en una matriz(ETD) con la informacion RGB de la imagen
def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))

# convierte una imagen tipo Imagen (de la libreria PIL) a imagen en Negativo
# procedimiento : multiplica por base 255 cada casilla de la matriz RGB para convertir la imagen en negativo

def invertirImgColores(img): # al parecer es la misma que el negativo
    n = img.size[0]
    m = img.size[1]
    for i in range(n):
        for j in range(m):
            # Obtenemos los colores RGB pixel por pixel
            r, g, b = img.getpixel((i, j))
            # Cambiamos el RGB del pixel
            img.putpixel((i, j), ((255-r), (255-g), (255-b)))
    return img

def main():
    starting_point=time.time() #Donde quiere empezar a calcular el tiempo
    img=Image.open("03.jpg") #abre imagen
    imgColor=invertirImgColores(img)
    imgColor.save("imageninvertida.png") #guarda la imagen con colores invertidos
    elapsed_time=time.time()-starting_point #calculo
    print ""
    print "Serial Time [seconds]: " + str(elapsed_time) #segundos

main()
