import mis_funciones as mf
import numpy as np
import cv2

camara = cv2.VideoCapture(1)

for aux in range(1000):
    _, image = camara.read()
    mask = mf.color_filter(image, "red")

    cv2.imshow("Original", image)
    # cv2.imshow("Mask", mask)
    # cv2.waitKey(0)

    [centroide, cnts] = mf.get_centroid(mask, "contorno")
    cX = centroide[0][0]
    cY = centroide[0][1]


    # Hacer lista con coord horizontales y lista con pares x,y
    if len(cnts) == 0:
        continue

    cnt = cnts[0]
    # puntos_hor = []
    puntos_lista = []
    for punto in cnt:
        # puntos_hor.append(punto[0][0])
        puntos_lista.append(punto[0][:])
       
    # Restricción eje vertical ("y" de la imagen)
    lim_sup = cY + 20
    lim_inf = cY - 20
    puntos_lista = [p for p in puntos_lista if p[1]>lim_inf 
            and p[1]<lim_sup]


    # Restricción eje horizontal ("x" de la imagen)
    mayor = 0
    menor = 10*image.shape[1]
    for punto in puntos_lista:
        if punto[0] > mayor:
            mayor = punto[0]
        
        if punto[0] < menor:
            menor = punto[0]

        
    # El punto de agarre a la derecha es aprox [mayor, cY]
    offset_hor = 25
    punto_derecho = [mayor+offset_hor, cY]


    # El punto de agarre a la izquierda es aprox [menor, cY]
    offset_hor = -25
    punto_izquierdo = [menor+offset_hor, cY]

    # La máscara como imagen de 3 canales
    clone = mask.copy()*255
    clone = cv2.merge((clone, clone, clone))

    # Dibujo de círculo y contorno
    cv2.drawContours(clone, [cnt], -1, (255, 0, 0), 3)
    cv2.circle(clone, tuple(punto_derecho), 5, (0, 255, 0), -1)
    cv2.circle(clone, tuple(punto_izquierdo), 5, (0, 0, 255), -1)
    # pos_texto_der = (mayor - 50, cY - 15)
    cv2.putText(clone, "Rojo: izquierda\nVerde: derecha", (20, 40), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    cv2.imshow("Punto Derecho", clone)
    cv2.waitKey(1)

camara.release()

