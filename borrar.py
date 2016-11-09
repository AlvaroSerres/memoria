from mis_funciones import Mano
from controladores import Ctrl_Pulgar
import time
import cv2

camara = cv2.VideoCapture(1)
mano = Mano(camara)

ctrl = Ctrl_Pulgar()

print("Explorando...")
ctrl.explorar(camara, mano)

punto_objetivo = [240, 250]
print("Calculando...")
ctrl.mover(punto_objetivo, camara, mano)

time.sleep(1)

punto_objetivo = [260, 250]
print("Calculando...")
ctrl.mover(punto_objetivo, camara, mano)
