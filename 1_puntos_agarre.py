import mis_funciones as mf
import numpy as np
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
        help="Path to the image file")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])
cv2.imshow("Original", image)

mask = mf.color_filter(image, "green")
cv2.imshow("Mask", mask)
cv2.waitKey(0)

[centroide, cnts] = mf.get_centroid(mask, "contorno")
cX = centroide[0][0]
cY = centroide[0][1]
print("------------------------------------------")
print("[DEBUG] centroide: {}".format(centroide))

# print("Size cnts: {}".format(len(cnts)))
# print("Size cnts[0]: {}".format(len(cnts[0])))
# print("Size cnts[0][0]: {}".format(len(cnts[0][0])))

# Hacer lista con coord horizontales y lista con pares x,y
cnt = cnts[0]
# puntos_hor = []
puntos_lista = []
for punto in cnt:
    # puntos_hor.append(punto[0][0])
    puntos_lista.append(punto[0][:])
   
# Restricción eje vertical ("y" de la imagen)
lim_sup = cY + 10
lim_inf = cY - 10
puntos_lista = [p for p in puntos_lista if p[1]>lim_inf 
        and p[1]<lim_sup]

print("------------------------------------------")
print("[DEBUG] puntos_lista: {}".format(puntos_lista))

# Restricción eje horizontal ("x" de la imagen)
mayor = 0
menor = 10*image.shape[1]
for punto in puntos_lista:
    if punto[0] > mayor:
        mayor = punto[0]
    
    if punto[0] < menor:
        menor = punto[0]

print("------------------------------------------")
print("[DEBUG] mayor: {}".format(mayor))
    
# El punto de agarre a la derecha es aprox [mayor, cY]
punto_derecho = [mayor, cY]

# El punto de agarre a la izquierda es aprox [menor, cY]
punto_izquierdo = [menor, cY]

# La máscara como imagen de 3 canales
clone = mask.copy()*255
clone = cv2.merge((clone, clone, clone))

# Dibujo de círculo y contorno
cv2.drawContours(clone, [cnt], -1, (255, 0, 0), 3)
cv2.circle(clone, tuple(punto_derecho), 5, (0, 255, 0), -1)
cv2.circle(clone, tuple(punto_izquierdo), 5, (0, 0, 255), -1)
# pos_texto_der = (mayor - 50, cY - 15)
# cv2.putText(clone, "Punto derecho", pos_texto_der, 
#         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

cv2.imshow("Punto Derecho", clone)
cv2.waitKey(0)



