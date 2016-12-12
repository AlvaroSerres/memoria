# Script para pruebas de captura y procesamiento de imagen

import mis_funciones as mf
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--color", required=True, 
        help="Color a filtrar (green, blue o red)")
args = vars(ap.parse_args())

camara = cv2.VideoCapture(1)

for i in range(3000):
    # Toma una foto
    # foto = mf.take_picture(camara)
    _, foto = camara.read()

    # Filtra por color 
    filtered = mf.color_filter(foto, args["color"])
    clone = filtered.copy()

    # Centroide
    # OJO: al usar método de contorno r es una lista de centroides
    r, cnts = mf.get_centroid(filtered, "contorno")
    mf.draw_circle(foto, r[0]) 
#   print(r)
#   cnts = mf.get_contours(filtered)
#   print("# de contornos: {}".format(len(cnts)))
    if cnts != 0:
        cv2.drawContours(foto, cnts, -1, (0, 255, 0), 3)

    # mf.show_picture(picture=picture, delay=1)
    cv2.imshow("Mask", clone)
    cv2.imshow("Foto", foto)

    # Esta espera es necesaria para que se puedan abrir las ventanas
    cv2.waitKey(1)

print("----------------------------------")
print("     T E R M I N A D O     ")
print("----------------------------------")

# cv2.waitKey(0)
cv2.destroyAllWindows()
camara.release()



""" O B S E R V A C I O N E S 

Para mostrar un video (feedbeack de tiempo real) se debe
usar la función camara.read() en vez de mf.take_picture()
debido a que esta última descarta las imágenes del buffer de la 
cámara (se produce submuestreo).

Hay dos formas (hasta ahora) de obtener el centroide a partir 
de la máscara, (1) por definición y calculo directo del centroide
usando los pixeles brutos de la máscara, o (2) encontrar el contorno
externo más grande en la máscara y calcular el centroide de ese
contorno con la ayuda de la función cv2.moments().

El segundo método para obtener el centroide debiese ser mejor 
para eliminar errores producidos por manchones negros en la másacara
y que quedan dentro del contorno.

* Falta implementar una diferenciación para las yemas verdes 

"""






