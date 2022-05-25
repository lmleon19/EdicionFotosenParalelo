import colorsys
from mpi4py import MPI
import numpy as np
from PIL import Image, ImageChops
import StringIO
from PIL import ImageEnhance
import time

comm = MPI.COMM_WORLD  # comunicador entre dos procesadores #

rank = comm.rank     # id procesador actual #
size = comm.size     # tamano procesador #

# propiedades de NP para cambiar de modo RGB a HSV y viceversa
rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

def convertirImgMatrixRGB(img):
    return np.array(img.convert("RGB"))



def union(arr):
    imagen = Image.fromarray(arr)
    imagen2=retoquecolor(imagen)
    imagen3=color(imagen2, 205)
    imagen4=blanquear(imagen3)
    #imagen5=tonos(imagen4)
    arr = convertirImgMatrixRGB(imagen4)

    return arr


#recibe un arreglo RGB de la imagen,lo convierte en negativo y retorna el arreglo negativo
def convertirImgNegativo(arrImg):
    for i in range(len(arrImg)): #largo
        for j in range(len(arrImg[0])):  #ancho
            arrImg[i][j] = 255-arrImg[i][j]
    return arrImg

# Resaltamos ciertos tonos como el rojo por sobre los demas para dar un efecto adicional
def retoquecolor(img):
	for i in range(img.size[0]):
		for j in range(img.size[1]):
			r, g, b = img.getpixel((i, j))
			img.putpixel((i, j), ((r+230)/3, (r+g+150)/3, (r+g+b+70)/3))
	return img


# funcion que blanquea las tonalidades verdes.
def blanquear(img):
	arrImg = convertirImgMatrixRGB(img)
	for i in range(img.size[1]):
		for j in range(img.size[0]):
			if(arrImg[i][j][1]>240 and arrImg[i][j][0]<80 and arrImg[i][j][2]<80):
				arrImg[i][j][0] =255
				arrImg[i][j][1] =255
				arrImg[i][j][2] =255
	imgblanqueada = Image.fromarray(arrImg)
	return imgblanqueada


# asigna mayor brillo y contraste a la imagen
def tonos(img):
    imgtono=ImageEnhance.Sharpness(img).enhance(4)
    imgtono=ImageEnhance.Brightness(img).enhance(700)
    imgtono=ImageEnhance.Contrast(img).enhance(3)
    return imgtono

# resaltamos matiz de la imagen
def color(imagen, matiz):
	img = imagen.convert('RGBA')
	arr = np.array(np.asarray(img).astype('float'))
	imgresaltada = Image.fromarray(cambiar_matiz(arr, matiz/360.).astype('uint8'), 'RGBA')

	return imgresaltada

# aplicamos grado de matiz al modo HSV
def cambiar_matiz(arr, grado_matiz):
    r, g, b, a = np.rollaxis(arr, axis=-1)
    h, s, v = rgb_to_hsv(r, g, b)
    h = grado_matiz
    r, g, b = hsv_to_rgb(h, s, v)
    arr = np.dstack((r, g, b, a))
    return arr


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
    starting_point=time.time()
    if rank==0:
        ruta="poto.jpg"
        divisionTareaImagen(ruta)
    if rank!=0:
        arrTrabajo=comm.recv(source=0)    #cada procesador recibe un arreglo RGB que contiene un trozo horizontal de la imagen
        arrImgSalida=union(arrTrabajo)    #enviar el arreglo RGB a transformarlo en arreglo negativo de la imagen
        comm.send(arrImgSalida,dest=0)
    if rank==0 :       #recibe los arreglos y los junta uno abajo del otro
        for i in range(1,size):
            if i > 1:
                construcImg = np.concatenate((construcImg,comm.recv(source=i)))
            if i == 1:
                construcImg = comm.recv(source=i)
        imgContrucFinal=Image.fromarray(construcImg)
        imgtono=ImageEnhance.Sharpness(imgContrucFinal).enhance(4)
        imgtono=ImageEnhance.Brightness(imgContrucFinal).enhance(700)
        imgtono=ImageEnhance.Contrast(imgContrucFinal).enhance(3)
        imgtono.save("IMAGENFINAL.png")

    elapsed_time=time.time()-starting_point

    print" "
    print "tiempo paralelo en segundos= " + str(elapsed_time)



main()
