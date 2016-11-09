"""
Script para controlar el dedo pulgar con 1 o 2 motores 
(el primer servo queda fijo)
"""

# --------------------------------------------------------------
# Importación de módulos
# --------------------------------------------------------------
import mis_funciones as mf
# import numpy as np
import controladores
import argparse
import cv2


# --------------------------------------------------------------
# Manejo de argumentos por línea de comando (shell)
# --------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("-g", "--guardar", required=False, action="store_true",
        help="Si se quiere guardar todos los atributos del controlador")

args = ap.parse_args()

# --------------------------------------------------------------
# Conexión de hardware y determinación de punto objetivo
# --------------------------------------------------------------
print("\tConectando cámara...")
camara = cv2.VideoCapture(1)

print("\tConectando mano...")
mano = mf.Mano(camara, pos_inicial_pulgar="arriba")

print("\tListo!\n")
print("---------------------------------------------------------------------")
print("\tPosiciona el objeto (rojo). Luego, presiona enter.")
print("---------------------------------------------------------------------")
_ = input()

# Posición objetivo
imagen = mf.take_picture(camara)

# Posición objetivo ahora es cercano al contorno, no el centroide
r_objetivo = mf.determinar_contacto(imagen, "pulgar")

print("\n\tPunto objetivo: {}".format(r_objetivo))

# --------------------------------------------------------------
# Control
# --------------------------------------------------------------
ctrl = controladores.Controlador("pulgar",
                                cantidad_motores, 
                                tercer_servo_auto=False,
                                yema_pulgar_visible=True,
                                )

# Exploración inicial (pasos = cantidad_motores)
ctrl.explorar(camara, mano)

# Evaluar el estado
estado = ctrl.evaluar_estado(r_objetivo)
print("Estado: {}".format(estado))

# Loop de cálculo de primitivas
while not ctrl.flags["_alcanzado_"]: 
    singular = ctrl.calcular_primitiva(r_objetivo, camara, mano)
    estado = ctrl.evaluar_estado(r_objetivo)
    print("Estado: {}".format(estado))

















