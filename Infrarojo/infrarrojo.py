import colorsys
import numpy as np
from PIL import Image, ImageEnhance
import time

# propiedades de NP para cambiar de modo RGB a HSV y viceversa
rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

# convertimos imagen a RGB para cambiar tonalidades rojas, azules y verdes.
def convertirImgMatrixRGB(img):
	return np.array(img.convert("RGB"))

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
	imgtono= ImageEnhance.Brightness(img).enhance(1000)
	imgtono= ImageEnhance.Contrast(img).enhance(3)
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

def main():
    #Asignamos un grado de matiz para resaltar colores
    starting_point=time.time()
    matiz=205
    img = Image.open('1.jpg')
    imgtocada=retoquecolor(img)
    imgcolor=color(imgtocada,matiz)
    imgblanc= blanquear(imgcolor)
    imgfinal= tonos(imgblanc)
    imgfinal.save("final.png")
    elapsed_time=time.time()-starting_point
    print" "
    print "tiempo serial en segundos= " + str(elapsed_time)
    
main()
