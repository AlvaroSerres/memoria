"""
Script para el control del dedo pulgar. Se debe colocar un objeto
rojo al alcance del dedo. 
"""

# --------------------------------------------------------------
# Importación de módulos
# --------------------------------------------------------------
import mis_funciones as mf
import controladores 
import argparse
import time
import cv2

# ================================================
# Manejo de argumentos por línea de comando (shell)
ap = argparse.ArgumentParser()
ap.add_argument("-g", "--guardar", required=False, action="store_true",
        help="Sólo explorar y guardar primitivas.")
ap.add_argument("-c", "--cargar", required=False,
        help="Extensión (número) del archivo de datos a cargar")

args = ap.parse_args()

def main(args):
    print("Iniciando...")
    # Argumentos
    guardar = args.guardar
    extension = args.cargar

    # =================================================
    # Inicialización hardware e instanciación controlador
    camara = cv2.VideoCapture(1)
    mano = mf.Mano(camara)
    ctrl = controladores.Ctrl_Pulgar()

    if guardar:
        # Comienzo de la exploración exhaustiva
        print("Exploración exhaustiva...")
        ctrl.explorar_ex(camara, mano)

        # Guardar las primitivas y terminar
        primitivas = mf.primitivas_np2list(ctrl.primitivas.copy())
        mf.guardar_datos("pulgar", primitivas)
        return

    # else: 
    datos = mf.cargar_datos("pulgar", extension)
    # si no se pudo cargar datos, termina
    if datos == None:
        return
    else:
        ctrl.primitivas = datos

    print("---------------------------------------------------------------------")
    print("\tPosiciona el objeto (rojo). Luego, presiona enter.")
    print("---------------------------------------------------------------------")
    _ = input()

    # =================
    # Posición objetivo
    imagen = mf.take_picture(camara)
    r_objetivo = mf.determinar_contacto(imagen, "pulgar", 
                                        offset_hor=15)
    print("Posición objetivo: {}".format(r_objetivo))
    print(r_objetivo)

    # ============================
    # Primer movimiento de la mano
    print("Calculando...")

    # Hay contacto yema-objeto?
    imagen = mf.take_picture(camara)
    contacto, dist = mf.hay_contacto(imagen, "pulgar", 
                                    kernel=[5,7])

    if not(contacto or (dist < 7)):
        ctrl.mover(r_objetivo, camara, mano)

        # OJO: la función mover del pulgar está pensado para 
        # mover el dedo sólo una vez y desde la posición inicial 
        # del dedo. Se asume que es suficiente, ya que su control 
        # es más sencillo (sólo se estima un servo). Luego hay que 
        # verificar si se alcanzó el objetivo (hay_contacto) y 
        # entrar en control_fino de ser necesario (muy probable,
        # ya que el objetivo de primer movimiento no es el objeto
        # sino un punto cercano a su contorno.

        ctrl.ajuste_fino(camara, mano)


# Llamado a main()
main(args)

print("===========================")
print("terminado")
print("===========================")






