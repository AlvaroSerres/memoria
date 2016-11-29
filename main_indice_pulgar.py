"""
Script para controlar los dedos índice y pulgar simultáneamente.
Se debe colocar un objeto rojo al alcance de los dedos.
"""

# --------------------------------------------------------------
# Importación de módulos
# --------------------------------------------------------------
import mis_funciones as mf
import controladores 
import argparse
# import time
import cv2

# ================================================
# Manejo de argumentos por línea de comando (shell)
ap = argparse.ArgumentParser()

ap.add_argument("-g", "--guardar", required=False, action="store_true",
        help="Controlar dedo y guardar primitivas.")

ap.add_argument("-ci", "--cargar_indice", required=False,
        help="Extensión (número) del archivo de datos a cargar (INDICE)")

ap.add_argument("-cp", "--cargar_pulgar", required=False,
        help="Extensión (número) del archivo de datos a cargar (PULGAR)")

args = ap.parse_args()

def main(args):
    print("Iniciando...")
    # Argumentos
    guardar= args.guardar
    extension_indice = args.cargar_indice
    extension_pulgar = args.cargar_pulgar

    # =================================================
    # Inicialización hardware e instanciación controlador
    camara = cv2.VideoCapture(1)
    mano = mf.Mano(camara,
                    pos_inicial_pulgar="arriba",
                    pos_inicial_indice="estirado",
                    )

    ctrl_indice = controladores.Ctrl_ERC(dedo="indice",
                                        tercer_servo_auto=True,
                                        )

    ctrl_pulgar = controladores.Ctrl_Pulgar()

    # NO HAY EXPLORACION EXHAUSTIVA EN ESTE SCRIPT
    # Cargar datos de primitivas en ambos dedos

    datos_indice = mf.cargar_datos("indice", extension_indice)
    datos_pulgar = mf.cargar_datos("pulgar", extension_pulgar)
    # si no se pudo cargar datos, termina
    if (datos_pulgar == None) or (datos_indice == None):
        print("No se pudo cargar datos...")
        return
    else:
        ctrl_indice.primitivas = datos_indice
        ctrl_pulgar.primitivas = datos_pulgar 
        primitivas_base_indice= len(datos_indice)
        primitivas_base_pulgar = len(datos_pulgar)

    print("---------------------------------------------------------------------")
    print("\tPosiciona el objeto (rojo). Luego, presiona enter.")
    print("---------------------------------------------------------------------")
    _ = input()

    # =================
    # Posición objetivo
    imagen = mf.take_picture(camara)
    r_objetivo_pulgar = mf.determinar_contacto(imagen, "pulgar", 
                                        offset_hor=15)

    r_objetivo_indice = mf.determinar_contacto(imagen, "indice")
    print("Posición objetivo indice: {}".format(r_objetivo_indice))
    print("Posición objetivo pulgar: {}".format(r_objetivo_pulgar))

    if (r_objetivo_indice == False) or (r_objetivo_indice == False):
        return 0

    # ============================
    # Primer movimiento de la mano
    print("Calculando...")

    # ===============================================
    # Hay contacto yema-objeto?
    imagen = mf.take_picture(camara)
    contacto, dist = mf.hay_contacto(imagen, "pulgar", 
                                    kernel=[5,7])

    # Mover pulgar al objetivo aproximado
    if not(contacto or (dist < 7)):
        ctrl_pulgar.mover(r_objetivo_pulgar, camara, mano)

    # Mover indice al objetivo aproximado
    while not ctrl_indice.flags["_alcanzado_"]: 
        # Ya no se necesita el flag de singular
        _ = ctrl_indice.calcular_primitiva(r_objetivo_indice, 
                                            camara, 
                                            mano,
                                            )

        # Verificación de objetivo alcanzado por medio de hay_contacto
        imagen = mf.take_picture(camara)
        _, dist = mf.hay_contacto(imagen, "indice")

        if dist < 30:
            break

        # Si no se pudo calcular la primitiva: explorar (paso = 1)
        if ctrl_indice.flags["_explorar_"]:
            ctrl_indice.explorar(camara, mano)

        estado = ctrl_indice.evaluar_estado(r_objetivo_indice)
        print("Estado: {}".format(estado))

    # Mover pulgar al objetivo final (contorno del objeto)
    print(" ")
    print("Ajustando dedo pulgar...")
    ctrl_pulgar.ajuste_fino(camara, mano)

    # Mover indice al objetivo final (contorno del objeto)
    print(" ")
    print("Ajustando dedo indice...")
    ctrl_indice.ajuste_fino(camara, mano)


    if guardar:
        # print("[DEBUG] Primitivas:\n")
        # print(ctrl.primitivas)

        primitivas_tray_indice = ctrl_indice.primitivas[primitivas_base_indice:]
        primitivas_tray_indice = mf.primitivas_np2list(primitivas_tray_indice)

        primitivas_tray_pulgar = ctrl_pulgar.primitivas[primitivas_base_pulgar:]
        primitivas_tray_pulgar = mf.primitivas_np2list(primitivas_tray_pulgar)

        # OJO: Las magnitudes, diferencias y posiciones se están
        # guardando como listas en lugar de numpy arrays.
        datos_pulgar = {"dedo": "pulgar",
                    "r_objetivo": [int(r_objetivo_pulgar[0]),int(r_objetivo_pulgar[1])],
                    "primitivas": primitivas_tray_pulgar,
                    }

        datos_indice = {"dedo": "indice",
                    "r_objetivo": [int(r_objetivo_indice[0]),int(r_objetivo_indice[1])],
                    "tercer_servo_auto": ctrl_indice.tercer_servo_auto,
                    "cantidad_motores": ctrl_indice.cantidad_motores,
                    "primitivas": primitivas_tray_indice,
                    }

        mf.guardar_datos(nombre="indice_pulgar", 
                      datos=[datos_indice, datos_pulgar],
                      directory="trayectorias_2_dedos/",
                      )


# Llamado a main()
main(args)

print("===========================")
print("terminado")
print("===========================")






