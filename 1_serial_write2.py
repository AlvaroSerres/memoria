# Este borrador se comunica correctamente con el Arduino Uno
# (serial_read_2). Se transfiere un string de largo variable
# con un caracter "terminador" (\n). 

import serial
import time

try:
    ser = serial.Serial()
    ser.port = '/dev/ttyACM0'
    ser.open()

except serial.serialutil.SerialException:
    print('El puerto no puede abrirse!')

else:
    # Si el puerto puede abrirse, se escribirá
    while True:
        ser.write(b'encendido\n')
        time.sleep(1)
        ser.write(b'apagado\n')
        time.sleep(1)

ser.close()
