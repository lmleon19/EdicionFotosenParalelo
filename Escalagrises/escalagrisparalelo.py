
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

def escalaGrises(imagen):
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

def main():
    starting_point=time.time()
    
    if rank == 0:
        ruta="1.jpg"
        divisionTareaImagen(ruta)

    if rank != 0:
        arrTrabajo = comm.recv(source = 0)    #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        arrImgSalida = escalaGrises(arrTrabajo)    #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen
        comm.send(arrImgSalida,dest=0)

    if rank == 0:       #recibe los arreglos y los junta uno abajo del otro
        for i in range(1, size):
            if i > 1:
                construcImg = np.concatenate((construcImg, comm.recv(source = i)), axis=0)
            if i == 1:
                construcImg = comm.recv(source = i)
        imgContrucFinal = Image.fromarray(construcImg)
        imgContrucFinal.save("imagenescaladegrises.png")
        
    elapsed_time=time.time()-starting_point
    print ""
    print "Tiempo paralelo [s]: " + str(elapsed_time)

main()
