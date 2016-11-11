"""
En este script se implemeta la parte fundamental del 
control de ajuste fino para la mano (considerando dos
yemas verdes visibles). Se hace un or entre las máscaras
de filtrado verde y rojo, luego se busca que haya sólo una figura
(un contorno) con un área aproximadamente igual a la suma
entre (1) el área roja en la máscara roja y (2) el área verde
de la máscara verde (ambas yemas visibles).
"""
import mis_funciones as mf
import numpy as np
import argparse
import cv2

# ================================================================
# Handling de argumentos
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dedo", required=True,
        help="Verifica contacto entre objeto y el dedo especificado")
args = vars(ap.parse_args())

dedo = args["dedo"]

# ================================================================
# Cámara
camara = cv2.VideoCapture(1)

# Imagen: Foto de la mano
imagen = mf.take_picture(camara)
cv2.imshow("Foto", imagen)
cv2.waitKey(0)

# Máscara roja, contorno y  área
mascara_rojo = mf.color_filter(imagen, "red")
cnt_rojo = mf.get_contours(mascara_rojo.copy())
area_rojo = cv2.contourArea(cnt_rojo[0])
print("[DEBUG] Area rojo: {}".format(area_rojo))

# ================================================================
# OPCION: buscar lso dos contornos más grandes en la máscara verde
# Máscara verde, contornos y area
mascara_verde = mf.color_filter(imagen, "green")
r, _ = mf.get_centroid(mascara_verde)

# ================================================================
# Máscara derecha (yema índice)
mask_der = np.zeros(mascara_verde.shape[:2], dtype="uint8")
mask_der[:, r[0]:] = 255
mascara_verde_temp = mascara_verde.copy()

# DEBUG
# cv2.imshow("Máscara verde temp (1)", mascara_verde_temp)

yema_indice = cv2.bitwise_and(mascara_verde_temp, mascara_verde_temp, 
        mask=mask_der)

# DEBUG
# cv2.imshow("yema_indice", yema_indice)

# Ahora se obtiene el contorno de la yema indice (derecha)
_, cnt_verde_der = mf.get_centroid(yema_indice.copy(), method="contorno")
area_verde_der = cv2.contourArea(cnt_verde_der[0])

# ================================================================
# Máscara izquierda (yema pulgar)
mask_izq = np.zeros(mascara_verde.shape[:2], dtype="uint8")
mask_izq[:, :r[0]] = 255
mascara_verde_temp = mascara_verde.copy()

# DEBUG
# cv2.imshow("Máscara verde temp (2)", mascara_verde_temp)

yema_pulgar = cv2.bitwise_and(mascara_verde_temp, mascara_verde_temp, 
        mask=mask_izq)

# DEBUG
# cv2.imshow("yema_pulgar", yema_pulgar)

# Ahora se obtiene el contorno de la yema pulgar (izquierda)
_, cnt_verde_izq = mf.get_centroid(yema_pulgar.copy(), method="contorno")
area_verde_izq = cv2.contourArea(cnt_verde_izq[0])

# Área verde total:
area_verde = area_verde_izq + area_verde_der

print("[DEBUG] Area verde izq: {}".format(area_verde_izq))
print("[DEBUG] Area verde der: {}".format(area_verde_der))
print("[DEBUG] Area verde: {}".format(area_verde))

# ================================================================
# Dibujando los contornos (verdes y rojo)
imagen_copia = imagen.copy()
cv2.drawContours(imagen_copia, cnt_verde_izq, -1, (0, 255, 0), 3)
cv2.drawContours(imagen_copia, cnt_verde_der, -1, (0, 255, 0), 3)
cv2.drawContours(imagen_copia, cnt_rojo, -1, (0, 0, 255), 3)

cv2.imshow("Contornos", imagen_copia)
cv2.waitKey(0)


# ================================================================
# Máscara yema indice y rojo (para control del dedo índice)
# OBS: Esta máscara conjunta nunca muestra que haya contacto
# entre el cubo rojo (objeto) y la yema, debido a que se generan 
# sombras en el borde de la yema. Por esto, es necesario hacer
# algunas operaciones morfológicas de dilatación y erosión
# (closing)
#
# OBS: El éxito de este método y el ajuste (por medio del tamaño
# del elemento estructural de la operación morfológica) depende
# de la iluminación.

if dedo == "indice":
    mascara = cv2.bitwise_or(mascara_rojo, yema_indice)

elif dedo == "pulgar":
    mascara = cv2.bitwise_or(mascara_rojo, yema_pulgar)
    
cv2.imshow("Mascara General", mascara)
cv2.waitKey(0)

# Operación morfológica "closing" juntar la yema con el objeto
# Kernel de tamaño [3, 5] parece funcionar bien para la yema del 
# dedo índice. Sin embargo, para el dedo pulgar conviene usar
# un kernel más grande debido a las condiciones de luz (natural)

if dedo == "indice":
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 5))

elif dedo == "pulgar":
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 7))

mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

# Se quiere encontrar un solo gran contorno cuya área se aprox igual
# a la suma de las areas del objeto y la yema del índice
cnt_dedo_objeto = mf.get_contours(mascara.copy())
area_cnt = cv2.contourArea(cnt_dedo_objeto[0])

print("[DEBUG] Area Mascara Indice-Objeto: {}".format(area_cnt))

mascara = cv2.merge((mascara, mascara, mascara))
cv2.drawContours(mascara, cnt_dedo_objeto, -1, (255, 0, 0), 3)
cv2.imshow("Mascara General", mascara)

# Condición de área para el contorno encontrado
area_objetivo = area_verde_der + area_rojo
tolerancia = 0.02         # en "tanto por uno" 
if area_cnt > (1-tolerancia)*area_objetivo: 
    print("Hay contacto entre dedo y objeto!")
    # Dejar de mover el dedo, se alcanzó el objetivo
    
else:
    print("NO hay contacto!")
    # Seguir moviendo el dedo (restar al primer servo)
        

# ================================================================
# Encontrar la distancia minima entre contornos
cnt_rojo = cnt_rojo[0]
cnt_verde_izq = cnt_verde_izq[0]
cnt_verde_der = cnt_verde_der[0]
dist_minima = float("inf")

if dedo == "indice":
    for punto_1 in cnt_rojo:
        for punto_2 in cnt_verde_der:
            dist = np.linalg.norm(punto_1 - punto_2)
            if dist < dist_minima:
                dist_minima = dist

elif dedo == "pulgar":
    for punto_1 in cnt_rojo:
        for punto_2 in cnt_verde_izq:
            dist = np.linalg.norm(punto_1 - punto_2)
            if dist < dist_minima:
                dist_minima = dist

print("[DEBUG] Distancia mínima: {}".format(dist_minima))

# Para la función: 
#
# Usar la distancia mínima como un segundo chequeo. Por ejemplo,
# si la distancia mínima es menor a 4 pixeles, entonces sí hay 
# contacto. De hecho, se podría basar sólo en la distancia mínima
# para determinar si hay o no contacto.



cv2.waitKey(0)
