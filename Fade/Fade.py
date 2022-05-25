from PIL import Image
import numpy as np
from os import system
import time

#---valor porcentual con el que se oscurece la imagen------
#--- 0 para que sea completamente negro  y 1 para que------
#----la imagen quede igual---------------------------------
oscurecimiento = 0.6


#---------------------------------------------------------------------------------------
#-----------------se oscure la imagen pixel por pixel, sus entradas son-----------------
#-----------------la imagen y el %de oscurecimiento-------------------------------------
#---------------------------------------------------------------------------------------
def oscurecer(imagen,porcentaje):
    matrix = np.array(imagen.convert('RGB'))
    oscurecimiento = 1.000000 - porcentaje
    #print oscurecimiento
    for i in range(imagen.size[1]):
        for j in range(imagen.size[0]):
            oscuro = matrix[i][j]*oscurecimiento
            matrix[i][j] = oscuro
    imagenFade = Image.fromarray(matrix)
    return imagenFade
#---------------------------------------------------------------------------------------
#-----------ciclo encargado de iterar la imagen para que se trabaje --------------------
#-----------se generaran multiples copias-----------------------------------------------
#---------------------------------------------------------------------------------------
def cicloOscurecer(imagen, rango):
    for i in range(rango):
        #---obtiene % de oscurecimiento---
        porcentaje = (float((i+1))/float(rango))
        print porcentaje
        #----llama a la funcion---
        resultadoOscuro = oscurecer(imagen,porcentaje)
        #-----guarda la imagen obtenida----
        if i<9:
            resultadoOscuro.save('CopiasCache/resultadoCache00'+str(i+1)+'.jpg')
        else:
            if i<99:
                resultadoOscuro.save('CopiasCache/resultadoCache0'+str(i+1)+'.jpg')
            else:
                resultadoOscuro.save('CopiasCache/resultadoCache'+str(i+1)+'.jpg')




#el delay representa la pausa entre una imagen y otra y loop 0 especifica que el gif se repite en un bucle. *jpg tomara todos los archivos *jpg (para este caso, puede ser cualquier formato de imagen)

#---------------------------------------------------------------------------------------
#-----------------definir main, cargar imagenes y funciones-----------------------------
#---------------------------------------------------------------------------------------
def main():
    #---carga imagen---
    imagen = Image.open('imagenCache.jpg')
    imagen.save('CopiasCache/resultadoCache000.jpg')

    #----rango de 60 imagenes para el fade---
    rango = 30

    #---llamada al generador de imagenes----
    cicloOscurecer(imagen,rango)

    nombreSalida="Fade.gif"
    delay=10
    filepath="CopiasCache/*jpg"
    system('convert -delay %d -loop 0 %s %s ' % (delay,filepath,nombreSalida))

#---------------------------------------------------------------------------------------

starting_point=time.time() #Donde quiere empezar a calcular el tiempo
main()
elapsed_time=time.time()-starting_point #calculo
print ""
print "Serial Time [seconds]: " + str(elapsed_time) #segundos