"""
Script main para controlar el dedo ínidice con 2 o 3 motores
"""

# --------------------------------------------------------------
# Importación de módulos
# --------------------------------------------------------------
import mis_funciones as mf
# import numpy as np
import controlador
import argparse
import cv2


# --------------------------------------------------------------
# Manejo de argumentos por línea de comando (shell)
# --------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--motores", required=False,
        help="# de motores a controlar (2 o 3, 2 por defecto)")
ap.add_argument("-g", "--guardar", required=False, action="store_true",
        help="Si se quiere guardar todos los atributos del controlador")

args = ap.parse_args()

# Cantidad de motores
if args.motores == None:
    cantidad_motores = 2
else:
    cantidad_motores = int(args.motores)


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
# filtrada = mf.color_filter(imagen, "red")
# [r_objetivo, _] = mf.get_centroid(filtrada, method="contorno")

# Posición objetivo ahora es el contorno, no el centroide
r_objetivo = mf.determinar_contacto(imagen, "indice")

print("\n\tPunto objetivo: {}".format(r_objetivo))

# --------------------------------------------------------------
# Control
# --------------------------------------------------------------
ctrl = controlador.Controlador("indice",
                                cantidad_motores, 
                                tercer_servo_auto=True,
                                yema_pulgar_visible=True,
                                )

# Exploración inicial (pasos = cantidad_motores)
ctrl.explorar(camara, mano)

# Evaluar el estado
estado = ctrl.evaluar_estado(r_objetivo)
print("Estado: {}".format(estado))

# Loop de cálculo de primitivas
while not ctrl.flags["_alcanzado_"]: 
    # Ya no se necesita el flag de singular
    _ = ctrl.calcular_primitiva(r_objetivo, camara, mano)

    # Verificación de objetivo alcanzado por medio de hay_contacto
    imagen = mf.take_picture(camara)
    _, dist = mf.hay_contacto(imagen, "indice")

    if dist < 20:
        break

    # Si no se pudo calcular la primitiva: explorar (paso = 1)
    if ctrl.flags["_explorar_"]:
        ctrl.explorar(camara, mano)

    estado = ctrl.evaluar_estado(r_objetivo)
    print("Estado: {}".format(estado))

# ========================================================
# Ajuste "fino"
print(" ")
print("Ajustando dedo...")
ctrl.ajuste_fino(camara, mano)

# ========================================================
# Guardar datos al finalizar
if args.guardar:
    # JSON no permite guardar arreglos de numpy por lo que 
    # hay que convertirlos a lista antes de guardarlos.

    primitivas = ctrl.primitivas[:]
    primitivas = mf.primitivas_np2list(primitivas)

    # OJO: Las magnitudes, diferencias y posiciones se están
    # guardando como listas en lugar de numpy arrays.
    datos = {"dedo": ctrl.dedo,
            "yema_pulgar_visible": ctrl.yema_pulgar_visible,
            "tercer_servo_auto": ctrl.tercer_servo_auto,
            "cantidad_motores": ctrl.cantidad_motores,
            "primitivas": primitivas
            }

    mf.guardar_datos("indice", datos)




