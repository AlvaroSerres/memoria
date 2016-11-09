import numpy as np
import datetime
import time
import json

# Lectura de un archivo de texto plano -----------
try:
    with open("este_nombre_no_existe.txt") as file_object:
        lista = file_object.readlines()

except:
    #print("El archivo no se pudo abrir...")
    pass # Fail silencioso
else:
    print(lista)
# ------------------------------------------------

# Escritura con modulo json
    
today = datetime.datetime.today()
tt = today.timetuple()

# formato de fecha es yyyymmdd_hhmmss
filename = "datos_dedo_{:4d}{:02d}{:02d}_{:02d}{:02d}{:02d}"
filename = filename.format(tt.tm_year, tt.tm_mon, tt.tm_mday,
                            tt.tm_hour, tt.tm_min, tt.tm_sec)

print(filename)                            

filename = "datos_borrador/" + filename

array = np.arange(10).resize((2, 5))
lista = [1, 2, "a", [3, "q", 4, "e"], [1], 9, array]

with open(filename, "w") as file_object:
    json.dump(lista, file_object)

#time.sleep(2)
#
#with open(filename) as file_object:
    #datos = json.load(file_object)


