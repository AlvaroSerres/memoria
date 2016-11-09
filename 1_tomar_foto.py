import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
        help="Nombre de la foto")
args = vars(ap.parse_args())

camara = cv2.VideoCapture(1)
print("Tomando foto...")
_, foto = camara.read()

# Guardando la foto
cv2.imwrite(args["output"], foto)

# Mostrando la foto
cv2.imshow("Foto", foto)
cv2.waitKey(0)

print("Terminado: foto guardada...")

del(camara)
cv2.destroyAllWindows()

