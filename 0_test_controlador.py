# Script para pruebas de controladores

import mis_funciones as mf
import numpy as np
import controlador
import argparse
import serial
import cv2

# --------------------------------------------------
# Argument Parsing
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dedo", required=False,
        help="Dedo: pulgar, indice o anular.")
ap.add_argument("-m", "--motores", required=False,
        help="Cantidad de motores a usar")
args = vars(ap.parse_args())

print("Args['dedo']: {}".format(args["dedo"]))
print("Args['cantidad_motores']: {}".format(args["motores"]))

# --------------------------------------------------
# Conección de cámara y mano
print("\tConectando cámara...")
camara = cv2.VideoCapture(1)
print("\tConectando mano...")
mano = mf.Mano(camara)
print("\tListo!\n")

# Posición objetivo
imagen = mf.take_picture(camara)
filtrada = mf.color_filter(imagen, "red")
[r_objetivo, _] = mf.get_centroid(filtrada, method="contorno")
print("\n\tPunto objetivo: {}".format(r_objetivo))

# --------------------------------------------------
# Controlador basado en EnRoCo
print("\tInstanciando controlador...")
# Argumentos
if args["dedo"] == None:
    dedo = "indice"
else:
    dedo = args["dedo"]

if args["motores"] == None:
    cantidad_motores = 2
else:
    cantidad_motores = int(args["motores"])

# Instanciación
ctrl = controlador.Controlador(dedo, cantidad_motores)

ctd_motores = ctrl.cantidad_motores
dedo = ctrl.dedo
color = ctrl.color
primer_servo = ctrl.primer_servo

print("\tAtributos Iniciales:")
print("\t\t# Motores: {}".format(ctd_motores))
print("\t\tDedo: {}".format(dedo))
print("\t\tColor: {}".format(color))
print("\t\tPrimer Servo: {}".format(primer_servo))

# --------------------------------------------------
# Algunas etapas de exploración
print("\n\tPosición inicial dedo: [{}, {}, {}]".format(
        mano.entregar_dedo_pos(dedo)[0],
        mano.entregar_dedo_pos(dedo)[1],
        mano.entregar_dedo_pos(dedo)[2]))

for i in range(3):
    print("\n\tExploración #: {}\n".format(i+1))
    ctrl.explorar(camara, mano)

primitivas = ctrl.primitivas
print("\t\tPrimitivas:")
for j, primitiva in enumerate(primitivas):
    print("\n\t\tPrimitiva #{}".format(j+1))
    for key, value in primitiva.items():
        print("\t\t{}: {}".format(key, value))
    print(" ")


# --------------------------------------------------
# Agregar primitiva nueva (calculada)
print("Nuevas Primitivas")
# r_objetivo = np.array([30, 60]) # En coordenadas de imagen


# Calculadas con éxito
exito = 0
for i in range(3):
    singular = ctrl.calcular_primitiva(r_objetivo, camara, mano)
    estado = ctrl.evaluar_estado(r_objetivo)
    print("Estado: {}".format(estado))
    if not singular:
        exito += 1

primitivas = ctrl.primitivas
print("\n\tPrimitivas Calculadas con Éxito: {}/{}\n".format(exito, 3))

# Imprime las primitivas calculadas
for j, primitiva in enumerate(primitivas):
    if not primitiva["exploracion"]:
        print("\n\t\tPrimitiva #{}".format(j+1))
        for key, value in primitiva.items():
            print("\t\t{}: {}".format(key, value))
        print(" ")





