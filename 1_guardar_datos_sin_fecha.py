""" 
Un script rápido que permite ver el contenido de un 
directorio. Cada nombre de archivos, se guarda como srting 
en una lista.
"""

import pathlib

p = pathlib.Path("./datos_guardados")

archivos = []

for f in p.iterdir():
    archivos.append(str(f))
    print(f)

filename = "datos_guardados/datos_pulgar_20161110_131253"

if filename in archivos:
    print("\nEncontrado...")

else:
    print(archivos)
