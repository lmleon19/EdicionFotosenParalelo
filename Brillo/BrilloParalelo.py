from mpi4py import MPI
import numpy as np
from PIL import Image,ImageChops
import StringIO

comm = MPI.COMM_WORLD  # comunicador entre dos procesadores #

rank = comm.rank     # id procesador actual #
size = comm.size     # tamano procesador #


def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))

#Trabajando en como matriz siempre
def aplicarBrillo(arreglo,factor):
    img = Image.fromarray(arreglo)
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
    #imgBrillante=Image.fromarray(arrImg)#se devuelve la matriz a imagen
    #return imgBrillante
    return arrImg

#funcion que recibe la ruta de imagen y distribuye los trozos horizontales a cada procesador excepto el cero
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
    if rank==0:
        ruta="imagenMuestra.jpg"
        divisionTareaImagen(ruta) 
    if rank!=0:
        arrTrabajo=comm.recv(source=0)    #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        arrImgSalida=aplicarBrillo(arrTrabajo,0.5)    #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen
        comm.send(arrImgSalida,dest=0)
    if rank==0 :       #recibe los arreglos y los junta uno abajo del otro
        for i in range(1,size):
            if i > 1:
                construcImg = np.concatenate((construcImg,comm.recv(source=i)))


            if i == 1:
                construcImg = comm.recv(source=i)


        imgContrucFinal=Image.fromarray(construcImg)
        imgContrucFinal.save("resultado.jpg")



import time #Libreria
starting_point=time.time() #Donde quiere empezar a calcular el tiempo
main()
elapsed_time=time.time()-starting_point #calculo
print ""
print "Time [seconds]: " + str(elapsed_time) #segundos
