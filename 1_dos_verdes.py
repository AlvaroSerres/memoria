# La idea es separar dos objetos que se ven del mismo 
# color en la imagen (dos yemas verdes)

import mis_funciones as mf
import numpy as np
import cv2

camara = cv2.VideoCapture(1)

for i in range(20):
    image = mf.take_picture(camara)

    filtrada = mf.color_filter(image, "green")
    r = mf.get_centroid(filtrada)
    
    # Máscara para obtener uno de los dos objetos
    mask_izq = np.zeros(filtrada.shape[:2], dtype="uint8")
    mask_izq[:, :r[0]] = 255
    mask_der = cv2.bitwise_not(mask_izq)

    objeto_izq = cv2.bitwise_and(filtrada, mask_izq)
    objeto_der = cv2.bitwise_and(filtrada, filtrada, mask=mask_der)

    print("Foto #{:02d}".format(i))
#    cv2.imshow("mask_izq", mask_izq)
#    cv2.imshow("mask_der", mask_der)
#    cv2.imshow("Foto", image)
    cv2.imshow("Objeto Izquierdo", objeto_izq)
    cv2.imshow("Objeto Derecho", objeto_der)
    cv2.waitKey(1000)

cv2.waitKey(0)
cv2.destroyAllWindows()
camara.release()

