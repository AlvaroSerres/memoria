import mis_funciones as mf
import controladores
import cv2

camara = cv2.VideoCapture(1)
mano = mf.Mano(camara)
ctrl = controladores.Ctrl_ERC(tercer_servo_auto=True)

ctrl.explorar_ex(camara, mano)

print("Magnitudes generadas")

for primitiva in ctrl.primitivas:
    print(primitiva["magnitud"])
