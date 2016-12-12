"""Script de prueba para grabar video usando cámara logitech"""

import cv2

camara = cv2.VideoCapture(1)
fourcc = cv2.VideoWriter_fourcc(*"XVID")

# Tamaño del cuadro y FPS
ancho = int(camara.get(cv2.CAP_PROP_FRAME_WIDTH))
alto = int(camara.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(camara.get(cv2.CAP_PROP_FPS))

video = cv2.VideoWriter("Video_Mano.avi", fourcc, fps, (ancho, alto))

while(camara.isOpened()):
    ret, frame = camara.read()
    if ret == True:
        # se escribe un cuadro
        video.write(frame)

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    else:
        break

camara.release()
video.release()
cv2.destroyAllWindows()

