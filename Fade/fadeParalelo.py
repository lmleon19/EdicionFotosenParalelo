from PIL import Image
import numpy as np
from os import system
import time
from mpi4py import MPI

comm = MPI.COMM_WORLD  # comunicador entre dos procesadores
rank = comm.rank     # id procesador actual
size = comm.size     # cantidad de procesadores a usar

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
def cicloOscurecer(rango):
    for i in range(1,rango):
        #---obtiene % de oscurecimiento---
        porcentaje = (float((i+1))/float(rango))
        comm.send(porcentaje, dest = i)

#el delay representa la pausa entre una imagen y otra y loop 0 especifica que el gif se repite en un bucle. *jpg tomara todos los archivos *jpg (para este caso, puede ser cualquier formato de imagen)

#---------------------------------------------------------------------------------------
#-----------------definir main, cargar imagenes y funciones-----------------------------
#---------------------------------------------------------------------------------------
def main():
    #----rango de 60 imagenes para el fade---
    rango = 30
    if rank ==0:
        imagen = Image.open('imagenCache.jpg')
        imagen.save('CopiasCache/resultadoCache0.jpg')
        cicloOscurecer(size)
    if rank !=0:
        #---carga imagen---
        imagen = Image.open('imagenCache.jpg')
        porcentaje = comm.recv(source =0)
        imagen = oscurecer(imagen,porcentaje)
        im = np.array(imagen.convert('RGB'))
        comm.send(im, dest=0)

    if rank==0:
        #---llamada al generador de imagenes-----
        for i in range (1,size):
            ######QUEDA SOLO 1 ELEMENTO POR RECIBIR QUE ES LA PROBABILIDAD
            imagen = comm.recv(source = i)
            imagen = Image.fromarray(imagen)
            if i<10:
                imagen.save('CopiasCache/resultadoCache00'+str(i)+'.jpg')
            else:
                if i<100:
                    imagen.save('CopiasCache/resultadoCache0'+str(i)+'.jpg')
                else:
                    imagen.save('CopiasCache/resultadoCache'+str(i)+'.jpg')

        nombreSalida="Fade.gif"
        delay=10
        filepath="CopiasCache/*jpg"
        system('convert -delay %d -loop 0 %s %s ' % (delay,filepath,nombreSalida))
        elapsed_time=time.time()-starting_point #calculo
        print ""
        print "Serial Time [seconds]: " + str(elapsed_time) #segundos

#---------------------------------------------------------------------------------------

starting_point=time.time() #Donde quiere empezar a calcular el tiempo
main()