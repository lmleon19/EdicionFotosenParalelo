
from mpi4py import MPI
import numpy as np
from PIL import Image,ImageChops
import StringIO

comm = MPI.COMM_WORLD  # comunicador entre dos procesadores #

rank = comm.rank     # id procesador actual #
size = comm.size     # tamano procesador #


# largo=imgSize[1]
# ancho=imgSize[0]
# print "largo :",largo
# print "Ancho :",ancho



def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))

#aplicar reflejo
def aplicarReflejo(arreglo):
    img = Image.fromarray(arreglo)
    arrImg=convertirImgMatrixRGB(img)
    arrSize=arrImg.shape
    largo=arrSize[1]
    ancho=arrSize[0]
    arrFinal = np.array(Image.new("RGB",(largo,ancho)))
    i=ancho-1
    j=0
    u=0
    v=0
    while i>=0:
        while j<largo:
            aux=arrImg[i][j]
            arrFinal[u][v]=aux
            j+=1
            v+=1
        i-=1
        j=0
        u+=1
        v=0
    #imgFinal =np.vstack((arrImg,arrFinal))
    imgFinal= arrFinal
    #imgReflejo = Image.fromarray(imgFinal)
    #return imgReflejo
    return imgFinal

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
        ruta="1.jpg"
        divisionTareaImagen(ruta)
    if rank!=0:
        arrTrabajo=comm.recv(source=0)    #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        arrImgSalida=aplicarReflejo(arrTrabajo)    #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen
        comm.send(arrImgSalida,dest=0)
    if rank==0 :       #recibe los arreglos y los junta uno abajo del otro
        for i in range(1,size):
            if i > 1:
                construcImg = np.concatenate((comm.recv(source=i),construcImg))
            if i == 1:
                construcImg = comm.recv(source=i)
        img = Image.open("1.jpg")
        imgOriginal = convertirImgMatrixRGB(img)
        arreglo = np.vstack((imgOriginal,construcImg))
        imgContrucFinal=Image.fromarray(arreglo)
        #imgContrucFinal=Image.fromarray(construcImg)
        imgContrucFinal.save("IMAGENFINAL.png")


import time #Libreria
starting_point=time.time() #Donde quiere empezar a calcular el tiempo
main()
elapsed_time=time.time()-starting_point #calculo
print ""
print "Time [seconds]: " + str(elapsed_time) #segundos
