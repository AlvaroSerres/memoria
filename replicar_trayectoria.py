"""Script para repetir los movimientos guardados anteriormente
    (primitivas guardadas con main_indice_pulgar.py)."""

import mis_funciones as mf
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cargar", required=True, 
                help="Número (índice) de datos a cargar.")
args = vars(ap.parse_args())

extension = args["cargar"]

camara = cv2.VideoCapture(1)
mano = mf.Mano(camara,
                pos_inicial_indice="estirado",
                pos_inicial_pulgar="arriba",
                )

datos = mf.cargar_datos("indice_pulgar",
                        extension,
                        "trayectorias_2_dedos/",
                        )






camara.release()
