# Script para pruebas de la clase mano y comunicación serial
# jjcarvajal@miuandes.cl
# jjcarvajal@miuandes.cl
# jjcarvajal@miuandes.cl
# jjcarvajal@miuandes.cl
# jjcarvajal@miuandes.cl
# jjcarvajal@miuandes.cl
# jjcarvajal@miuandes.cl
# jjcarvajal@miuandes.cl
# jjcarvajal@miuandes.cl

import mis_funciones as mf
import numpy as np
import serial
import time
import cv2

camara = cv2.VideoCapture(1)
mano = mf.Mano(camara, puerto='/dev/ttyUSB0')
print(" ")

time.sleep(3)
# ---------------------------------
# Valores iniciales:
# ---------------------------------
pulgar = mano.pulgar_pos
indice = mano.indice_pos
anular = mano.anular_pos

yema_p = mano.yema_pulgar_pos
yema_i = mano.yema_indice_pos
yema_a = mano.yema_anular_pos

print("Valores iniciales:--------------\n")
print("\tPulgar_pos: {}".format(pulgar))
print("\tIndice_pos: {}".format(indice))
print("\tAnular_pos: {}\n".format(anular))

print("\tYema_pulgar: {}".format(yema_p))
print("\tYema_indice: {}".format(yema_i))
print("\tYema_anular: {}\n".format(yema_a))

time.sleep(3)
# ---------------------------------
# Ajustar dedo
# ---------------------------------
# pulgar = np.array([2000, 200, 250])
indice = np.array([1000, 300, 350])
# anular = np.array([500, 400, 450])

print("Valores nuevos:-----------------------------\n")
print("\tPulgar_pos (objetivo): {}".format(pulgar))
print("\tIndice_pos (objetivo): {}".format(indice))
print("\tAnular_pos (objetivo): {}\n".format(anular))

limitado = False
# limitado = mano.ajustar_dedo("pulgar", pulgar)
limitado = mano.ajustar_dedo("indice", indice) or limitado
# limitado = mano.ajustar_dedo("anular", anular) or limitado

mano.mover()

pulgar = mano.pulgar_pos
indice = mano.indice_pos
anular = mano.anular_pos

print("\tPulgar_pos: {}".format(pulgar))
print("\tIndice_pos: {}".format(indice))
print("\tAnular_pos: {}\n".format(anular))

print("\tLimitado?: {}\n".format(limitado))

mano.actualizar_yema(camara, "indice")
mano.actualizar_yema(camara, "pulgar")
mano.actualizar_yema(camara, "anular")

yema_p = mano.yema_pulgar_pos
yema_i = mano.yema_indice_pos
yema_a = mano.yema_anular_pos

print("\tYema_pulgar: {}".format(yema_p))
print("\tYema_indice: {}".format(yema_i))
print("\tYema_anular: {}\n".format(yema_a))


time.sleep(3)
# ---------------------------------
# Ajustar dedo fuera de limites (inferior)
# ---------------------------------
# pulgar = np.array([10, 20, 25])
indice = np.array([10, 30, 35])
# anular = np.array([10, 40, 45])

print("Valores nuevos:-----------------------------\n")
print("\tPulgar_pos (objetivo): {}".format(pulgar))
print("\tIndice_pos (objetivo): {}".format(indice))
print("\tAnular_pos (objetivo): {}\n".format(anular))

limitado = False
# limitado = mano.ajustar_dedo("pulgar", pulgar)
limitado = mano.ajustar_dedo("indice", indice) or limitado
# limitado = mano.ajustar_dedo("anular", anular) or limitado

mano.mover()

pulgar = mano.pulgar_pos
indice = mano.indice_pos
anular = mano.anular_pos

print("\tPulgar_pos: {}".format(pulgar))
print("\tIndice_pos: {}".format(indice))
print("\tAnular_pos: {}\n".format(anular))

print("\tLimitado?: {}\n".format(limitado))

mano.actualizar_yema(camara, "indice")
mano.actualizar_yema(camara, "pulgar")
mano.actualizar_yema(camara, "anular")

yema_p = mano.yema_pulgar_pos
yema_i = mano.yema_indice_pos
yema_a = mano.yema_anular_pos

print("\tYema_pulgar: {}".format(yema_p))
print("\tYema_indice: {}".format(yema_i))
print("\tYema_anular: {}\n".format(yema_a))


time.sleep(3)
# ---------------------------------
# Ajustar dedo fuera de limites (superior)
# ---------------------------------
# pulgar = np.array([5000, 5000, 5000])
indice = np.array([5000, 5000, 5000])
# anular = np.array([5000, 5000, 5000])

print("Valores nuevos:-----------------------------\n")
print("\tPulgar_pos (objetivo): {}".format(pulgar))
print("\tIndice_pos (objetivo): {}".format(indice))
print("\tAnular_pos (objetivo): {}\n".format(anular))

limitado = False
# limitado = mano.ajustar_dedo("pulgar", pulgar)
limitado = mano.ajustar_dedo("indice", indice) or limitado
# limitado = mano.ajustar_dedo("anular", anular) or limitado

mano.mover()

pulgar = mano.pulgar_pos
indice = mano.indice_pos
anular = mano.anular_pos

print("\tPulgar_pos: {}".format(pulgar))
print("\tIndice_pos: {}".format(indice))
print("\tAnular_pos: {}\n".format(anular))

print("\tLimitado?: {}\n".format(limitado))

mano.actualizar_yema(camara, "indice")
mano.actualizar_yema(camara, "pulgar")
mano.actualizar_yema(camara, "anular")

yema_p = mano.yema_pulgar_pos
yema_i = mano.yema_indice_pos
yema_a = mano.yema_anular_pos

print("\tYema_pulgar: {}".format(yema_p))
print("\tYema_indice: {}".format(yema_i))
print("\tYema_anular: {}\n".format(yema_a))




