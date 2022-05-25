import ImageFilter
import numpy as np
import time
from numpy import array, shape, reshape, zeros, transpose
from PIL import Image, ImageChops, ImageOps

# convierte una imagen tipo Imagen (de la libreria PIL) en una matriz(ETD) con la informacion RGB de la imagen
def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))
    
def escalaGrises(img):
    n = img.size[0]
    m = img.size[1]
    for i in range(n):
        for j in range(m):
            # Obtenemos los colores RGB pixel por pixel
            r, g, b = img.getpixel((i, j))
            # Cambiamos el RGB del pixel
            img.putpixel((i, j), ((r+g+b)/3, (r+g+b)/3, (r+g+b)/3))
    return img
 
def main():
    starting_point=time.time() #Donde quiere empezar a calcular el tiempo
    img=Image.open("1.jpg") #abre imagen
    imgGris = escalaGrises(img)
    imgGris.save("imagenescaladegrispng") #guarda la imagen en escala de grises
    elapsed_time=time.time()-starting_point #calculo
    print ""
    print "Serial Time [seconds]: " + str(elapsed_time) #segundos
    
main()
