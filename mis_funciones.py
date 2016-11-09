# Este modulo contiene funciones útilizadas para 
# el control visual de la mano de tres dedos
import numpy as np
import datetime
import serial
import time
import json
import cv2

def take_picture(camera):
    """Toma una foto con la cámara especificada"""
    # La gracia de esta función es que descarta el buffer de 
    # la cámara
    for i in range(6):
        grabbed, picture = camera.read()
    return picture


def show_picture(picture, nombre_ventana="Imagen",  delay=10):
    """Abre una ventana y muestra una imagen por 10 ms
       a menos que se especifique otro tiempo de espera"""
    cv2.imshow(nombre_ventana, picture)
    cv2.waitKey(delay)
#    if delay == 0:
#        cv2.destroyAllWindows()


def color_filter(image, color):
    """Filtra por color especificado (método HSV)"""
    # Definicion de colores 
    if color == "blue":
        lower = np.array([110, 90, 30])
        upper = np.array([130, 255, 255])
    
    elif color == "green":
        lower = np.array([40, 90, 30])
        upper = np.array([75, 255, 255])
   
    else: # red
        color = "red"
        lower_2 = np.array([160, 90, 30])
        upper_2 = np.array([180, 255, 255])

        lower_1 = np.array([0, 90, 30])
        upper_1 = np.array([10, 255, 255])

    # Filtro pasa bajos (gaussiano)
    blurred = cv2.GaussianBlur(image, (9, 9), 0)
    # Conversión de color a HSV
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # Máscara
    if color == "red":
        mask_1 = cv2.inRange(hsv, lower_1, upper_1)
        mask_2 = cv2.inRange(hsv, lower_2, upper_2)
        mask = cv2.bitwise_or(mask_1, mask_2)
    else:
        mask = cv2.inRange(hsv, lower, upper)

    # Operación morfológica "opening" para eliminar "blobs"
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # Se devuelve la máscara (no hay necesidad de aplicarla)
    return mask
    

def get_contours(image, length=1):
    """Entrega el (los) contorno(s) exterior(es) más grande(s)"""
    # Por defecto sólo entrega un contorno (el más grande)
    (_, cnts, _) = cv2.findContours(image, cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE)
    # Chequear que se haya encontrado contornos 
    if len(cnts) != 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:length]
    return cnts


def get_centroid(image, method="propio"):
    """Obtiene el centroide de una imagen binaria"""
    # ---------Método Propio (directo de la definición)----------
    if method == "propio":
        # Dimensiones
        height, width = image.shape[:2]
        # Masa total
        total_mass = image.sum()

        # Si la masa total es cero, entonces el centro de masa 
        # no existe
        if total_mass == 0:
            r = np.array([-1, -1])
            return r, None

        # Primera componente (suma por filas)
        row_sum = image.sum(axis=1)
        row_weight = np.arange(1, height+1)
        r_i = np.dot(row_sum, row_weight)
        r_i /= total_mass
        r_i = int(r_i)
        
        # Segunda componente (suma por columnas)
        column_sum = image.sum(axis=0)
        column_weight = np.arange(1, width+1)
        r_j = np.dot(column_sum, column_weight)
        r_j /= total_mass
        r_j = int(r_j)

        # Retorna el centroide en coordenadas de imagen
        r = np.array([r_j, r_i])
        return r, None

    # ---------Método con contornos-----------------
    else:
        # Obtener contorno imagen binaria (máscara)
        cnts = get_contours(image)
        
        # Para cada contorno, obtener el centroide y añadirlo a lista
        r = []
        for c in cnts:
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            r.append(np.array([cX, cY]))

        # Ahora se retorna una lista con centroides (según la 
        # cantidad de contornos que se hayan encontrado)
        if len(r) == 0:
            r.append(np.array([-1, -1]))
            return r, cnts
        else:
            return r, cnts
           

def draw_circle(image, centroid, color="green", radius=5):
    """Dibuja centroide de color en la imagen"""
    # Revisar si el centroide existe
    if centroid[0]<0 or centroid[1]<0: 
        done = False
        return done

    # Color del círculo
    if color == "green":
        (b, g, r) = (0, 255, 0)

    elif color == "blue":
        (b, g, r) = (255, 0, 0)

    else:
        (b, g, r) = (0, 0, 255)
   
    # Dibujo del círculo
    cv2.circle(image, tuple(centroid), radius, (b, g, r), -1)
    done = True
    return done


def determinar_contacto(imagen, dedo, offset_hor=25):
    """Encuentra el punto de contacto izquierdo o derecho
    para agarrar el objeto (según lo que se pueda ver con la 
    cámara)"""
    # Filtrar la imagen por color ROJO (objeto)
    mask = color_filter(imagen, "red")

    # Obtener centroide y contorno del objeto
    [centroide, cnts] = get_centroid(mask, "contorno")
    cX = centroide[0][0]
    cY = centroide[0][1]

    # El contorno más grande que se encontró
    cnt = cnts[0]
    # Lista de puntos de contorno
    puntos_lista = []
    for punto in cnt:
        puntos_lista.append(punto[0][:])
       
    # Restricción eje vertical ("y" de la imagen)
    lim_sup = cY + 20
    lim_inf = cY - 20
    puntos_lista = [p for p in puntos_lista if p[1]>lim_inf 
            and p[1]<lim_sup]

    # Restricción eje horizontal ("x" de la imagen)
    mayor = 0
    menor = 10*mask.shape[1]
    for punto in puntos_lista:
        if punto[0] > mayor:
            mayor = punto[0]
        
        if punto[0] < menor:
            menor = punto[0]

    # El punto de agarre a la DERECHA es aprox [mayor, cY]
    if dedo=="indice" or dedo=="anular":
        punto_agarre = [mayor+offset_hor, cY]

    # El punto de agarre a la IZQUIERDA es aprox [menor, cY]
    elif dedo=="pulgar":
        punto_agarre = [menor-offset_hor, cY]

    # Retorna el punto de agarre derecho o izquierdo según el dedo
    return punto_agarre


def guardar_datos(nombre, datos):
    """Guarda los datos en formato json""" 
    today = datetime.datetime.today()
    tt = today.timetuple()
    # Directorio en donde guardar
    directory = "datos_guardados/"
    # Primera parte del nombre
    filename_1 = "datos_"
    # Tercera parte del nombre (fecha)
    # Formato de fecha es yyyymmdd_hhmmss
    filename_3 = "_{:4d}{:02d}{:02d}_{:02d}{:02d}{:02d}"
    filename_3 = filename_3.format(tt.tm_year, tt.tm_mon, tt.tm_mday,
                            tt.tm_hour, tt.tm_min, tt.tm_sec)

    # Nombre completo
    filename = directory + filename_1 + nombre + filename_3

    # Escritura de datos (módulo json)
    with open(filename, "w") as file_object:
        json.dump(datos, file_object)
    
    # Mensaje de escritura
    print("---------------------------------------")
    print("Datos escritos en:")
    print("\t" + filename)
    print("---------------------------------------")


def primitivas_np2list(primitivas):
    """Convierte los arreglos numpy a lista para poder
    ser guardados en formato JSON"""
    for primitiva in primitivas:
        for key, value in primitiva.items():
            if key[:3]=="pos" or key[:3]=="mag" or key[:3]=="dif":
                try:
                    value_temp = value.tolist()
                except AttributeError:
                    # pass
                    continue
                else:
                    primitiva[key] = value_temp 

    return primitivas


def hay_contacto(imagen, dedo):
    """Determina si hay contacto entre el objeto (rojo) y el 
    dedo especificado. La imagen de entrada es BGR. 
    Retorna un booleano y la distancia mínima entre 
    contornos"""
    # Máscara roja, contorno y  área
    mascara_rojo = color_filter(imagen, "red")
    cnt_rojo = get_contours(mascara_rojo.copy())
    area_rojo = cv2.contourArea(cnt_rojo[0])
    # print("[DEBUG] Area rojo: {}".format(area_rojo))

    # ================================================================
    # Máscara verde, contornos y area
    mascara_verde = color_filter(imagen, "green")
    r, _ = get_centroid(mascara_verde)

    # ================================================================
    # Máscara derecha (yema índice)
    if dedo == "indice":
        mask_der = np.zeros(mascara_verde.shape[:2], dtype="uint8")
        mask_der[:, r[0]:] = 255
        mascara_verde_temp = mascara_verde.copy()

        yema_indice = cv2.bitwise_and(mascara_verde_temp, mascara_verde_temp, 
                mask=mask_der)

        # Ahora se obtiene el contorno de la yema indice (derecha)
        _, cnt_verde = get_centroid(yema_indice.copy(), method="contorno")
        area_verde = cv2.contourArea(cnt_verde[0])

    # ================================================================
    # Máscara izquierda (yema pulgar)
    elif dedo == "pulgar":
        mask_izq = np.zeros(mascara_verde.shape[:2], dtype="uint8")
        mask_izq[:, :r[0]] = 255
        mascara_verde_temp = mascara_verde.copy()

        yema_pulgar = cv2.bitwise_and(mascara_verde_temp, mascara_verde_temp, 
                mask=mask_izq)

        # Ahora se obtiene el contorno de la yema pulgar (izquierda)
        _, cnt_verde = get_centroid(yema_pulgar.copy(), method="contorno")
        area_verde = cv2.contourArea(cnt_verde[0])
    
    else:
        print("[ERROR] 'hay_contacto' no está implementada para el dedo anular")

    # print("[DEBUG] Area verde: {}".format(area_verde))

    # ================================================================
    # Máscara yema indice y rojo (para control del dedo índice)
    # OBS: Esta máscara conjunta nunca muestra que haya contacto
    # entre el cubo rojo (objeto) y la yema, debido a que se generan 
    # sombras en el borde de la yema. Por esto, es necesario hacer
    # algunas operaciones morfológicas de dilatación y erosión
    # (closing)
    #
    # OBS: El éxito de este método y el ajuste (por medio del tamaño
    # del elemento estructural de la operación morfológica) depende
    # de la iluminación.

    if dedo == "indice":
        mascara = cv2.bitwise_or(mascara_rojo, yema_indice)

    elif dedo == "pulgar":
        mascara = cv2.bitwise_or(mascara_rojo, yema_pulgar)
        
    # Operación morfológica "closing": juntar la yema con el objeto
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 5))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)

    # Se quiere encontrar un solo gran contorno cuya área se aprox igual
    # a la suma de las areas del objeto y la yema 
    cnt_dedo_objeto = get_contours(mascara.copy())
    area_cnt = cv2.contourArea(cnt_dedo_objeto[0])

    # print("[DEBUG] Area Mascara Indice-Objeto: {}".format(area_cnt))

    # ================================================================
    # Encontrar la distancia minima entre contornos
    cnt_rojo = cnt_rojo[0]
    cnt_verde = cnt_verde[0]
    dist_minima = float("inf")

    for punto_1 in cnt_rojo:
        for punto_2 in cnt_verde:
            dist = np.linalg.norm(punto_1 - punto_2)
            if dist < dist_minima:
                dist_minima = dist

    print("[DEBUG] Distancia mínima: {}".format(dist_minima))

    # ================================================================
    # ------------ C O N D I C I O N E S --------------

    # Inicialización de flag de contacto
    contacto = None

    # Condición de puntos más cercanos
    if dist_minima < 3:
        contacto = True
        return contacto, dist_minima

    elif dist_minima > 7:
        contacto = False
        return contacto, dist_minima
   
    # Condición de área para el contorno encontrado
    area_objetivo = area_verde + area_rojo
    tolerancia = 0.02         # en "tanto por uno" 

    if area_cnt > (1-tolerancia)*area_objetivo: 
        contacto = True
        return contacto, dist_minima
    else:
        contacto = False
        return contacto, dist_minima

    



# ============================================
# --------------- C L A S E -----------------
# ============================================

class Mano():
    """Modelado simple de la mano de tres dedos"""

    def __init__(self,
            camara,
            puerto ='/dev/ttyUSB0',
            # Para que el pulgar quede hacia arriba
            pos_inicial_pulgar="arriba",
            ):
        """Inicialización de la mano (atributos)"""
            
        if pos_inicial_pulgar == "arriba" or pos_inicial_pulgar == "medio":
            self.yema_pulgar_visible=True

        else:
            self.yema_pulgar_visible=False


        # Posiciones iniciales   
        if pos_inicial_pulgar == "arriba":
            # Pulgar hacia arriba (yema visible)
            self.pulgar_pos = np.array([1600, 212, 512])
        
        elif pos_inicial_pulgar == "medio":
            # Pulgar en posición media (yema visible)
            self.pulgar_pos = np.array([1850, 212, 512])
       
        else:
            # Pulgar hacia abajo (yema no visible)
            self.pulgar_pos = np.array([2350, 212, 212])

        self.indice_pos = np.array([1600, 400, 200])
        self.anular_pos = np.array([512, 520, 350])
        
        # Posiciones límite
        self.pulgar_pos_lim = np.array([[825, 200, 200], [2350, 513, 513]])
        self.indice_pos_lim = np.array([[200, 200, 200], [2100, 550, 550]])
        self.anular_pos_lim = np.array([[200, 200, 200], [550, 550, 513]])

        # Posición de cada yema en la imagen
        self.yema_pulgar_pos = np.array([0, 0])
        self.yema_indice_pos = np.array([0, 0])
        self.yema_anular_pos = np.array([0, 0])

        # Puerto serial del controlador
        self.puerto = puerto

        # Acciones iniciales
        self.mover(comienza=True)
        self.actualizar_yema(camara, "indice")
        self.actualizar_yema(camara, "pulgar")
        self.actualizar_yema(camara, "anular")


    def entregar_dedo_pos(self, dedo="indice"):
        """Recibe un string dedo y devuelve su posición"""
        if dedo == "pulgar":
            posicion = self.pulgar_pos
        
        elif dedo == "anular":
            posicion = self.anular_pos

        else: 
            posicion = self.indice_pos

        return posicion


    def ajustar_dedo(self, dedo, posicion):
        """Cambia el atributo de posición para el dedo especificado"""
        # Limitados indica qué servo llegó al límite
        # Aumentar el ángulo abre la mano, disminuir el 
        # ángulo cierra la mano.
        limitado = False
        limitados_inf = [False]*3
        limitados_sup = [False]*3
        # Revisar que esté dentro de los límites
        if dedo == "indice":
            limites_sup = self.indice_pos_lim[1, :]
            limites_inf = self.indice_pos_lim[0, :]
            for i in range(0, 3):
                # Limite superior
                if posicion[i] > limites_sup[i]:
                    posicion[i] = limites_sup[i]
                    limitados_sup[i] = True
                # Límite inferior
                if posicion[i] < limites_inf[i]:
                    posicion[i] = limites_inf[i]
                    limitados_inf[i] = True
            # Atributo actualizado
            self.indice_pos = posicion
        
        # Se repite para otro dedo
        elif dedo == "pulgar":
            limites_sup = self.pulgar_pos_lim[1, :]
            limites_inf = self.pulgar_pos_lim[0, :]
            for i in range(0, 3):
                # Limite superior
                if posicion[i] > limites_sup[i]:
                    posicion[i] = limites_sup[i]
                    limitados_sup[i] = True
                # Límite inferior
                if posicion[i] < limites_inf[i]:
                    posicion[i] = limites_inf[i]
                    limitados_inf[i] = True
            # Atributo actualizado
            self.pulgar_pos = posicion

        # Se repite para otro dedo
        elif dedo == "anular":
            limites_sup = self.anular_pos_lim[1, :]
            limites_inf = self.anular_pos_lim[0, :]
            for i in range(0, 3):
                # Limite superior
                if posicion[i] > limites_sup[i]:
                    posicion[i] = limites_sup[i]
                    limitados_sup[i] = True
                # Límite inferior
                if posicion[i] < limites_inf[i]:
                    posicion[i] = limites_inf[i]
                    limitados_inf[i] = True
            # Atributo actualizado
            self.anular_pos = posicion
        
        # Retorno flag de limitación
        print("[DEBUG] Dedo: {}, Posición: {}".format(dedo, posicion))
        limitado = any(limitados_sup) or any(limitados_inf)
        return limitado, limitados_sup, limitados_inf


    def actualizar_yema(self, camara, dedo):
        """Actualiza la información de posición de cada yema"""

        if dedo == "indice":
            if self.yema_pulgar_visible:
                # Toma una foto/filtra por color/centroide (imagen completa)
                picture = take_picture(camara)
                filtrada = color_filter(picture, "green")
                r, _ = get_centroid(filtrada)

                # El dedo índice está a la derecha en la imagen
                mask_der = np.zeros(filtrada.shape[:2], dtype="uint8")
                mask_der[:, r[0]:] = 255
                yema_indice = cv2.bitwise_and(filtrada, filtrada, 
                        mask=mask_der)
                
                # Ahora se obtiene el centroide de la yema indice
                r, _ = get_centroid(yema_indice, method="contorno")
                r = r[0]
                self.yema_indice_pos = r

            else:
                # Toma una foto/filtra por color/centroide 
                picture = take_picture(camara)
                filtrada = color_filter(picture, "green")
                # Ahora se obtiene el centroide de la yema indice
                r, _ = get_centroid(filtrada, method="contorno")
                r = r[0]
                self.yema_indice_pos = r

        elif dedo == "pulgar":
            # Toma una foto/filtra por color/centroide (imagen completa)
            picture = take_picture(camara)
            filtrada = color_filter(picture, "green")
            r, _ = get_centroid(filtrada)

            # El dedo pulgar está a la izquierda en la imagen
            mask_izq = np.zeros(filtrada.shape[:2], dtype="uint8")
            mask_izq[:, :r[0]] = 255
            yema_pulgar = cv2.bitwise_and(filtrada, filtrada, 
                    mask=mask_izq)
            
            # Ahora se obtiene el centroide de la yema pulgar
            r, _ = get_centroid(yema_pulgar, method="contorno")
            r = r[0]
            self.yema_pulgar_pos = r

        elif dedo == "anular":
            # Toma una foto/filtra/centroide
            picture = take_picture(camara)
            filtrada = color_filter(picture, "blue")
            r, _ = get_centroid(filtrada, method="contorno")
            r = r[0]
            self.yema_anular_pos = r

        # Retorna la posición de la yema
        return r


    def mover(self, comienza=False):
        """Mover la mano según la posición dada a cada dedo
        (la idea es ajustar_posicion y luego mover)"""
        # Si es que mueve por primera vez hay que enviar el
        # string "Comienza" primero
        if comienza:
            mensaje = "Comienza"
            time.sleep(3)
            enviar_serial(self.puerto, mensaje)

        # Se obtiene la posición de cada dedo (lectura de atributos)
        pulgar = self.pulgar_pos
        indice = self.indice_pos
        anular = self.anular_pos
        # Se formatea el mensaje a enviar al controlador
        formateado = formatear(pulgar, indice, anular)
        # Luego, se envía el string formateado
        enviar_serial(self.puerto, formateado)

        



# ----------------- F I N    C L A S E -------------

def formatear(pulgar, indice, anular):
    """Formatea los arreglos de posición en un sólo string"""
    # Inicialización del string formateado
    formateado = ''
    # Lista de dedos
    dedos = [pulgar, indice, anular]
    # Padding con ceros, 4 dígitos, decimal
    for dedo in dedos:
        temp = "{:04d},{:04d},{:04d},".format(dedo[0], dedo[1], dedo[2])
        formateado += temp
    # Retorna el string formateado, sin la última coma
    return formateado[:-1]


def enviar_serial(puerto, mensaje, baudrate=57600):
    """Envía el string mensaje al dispositivo serial"""
    # Tratar de abrir el puerto serial
    try:
        ser = serial.Serial()
        ser.port = puerto
        # El baudrate del controlador es de 57600
        ser.baudrate = baudrate
        ser.open()

    except serial.serialutil.SerialException:
        print("\n-----------------------------------------------")
        print("\tEl puerto serial no puede abrirse!")
        print("-----------------------------------------------\n")

    else:
        # Se debe agregar un salto de línea al final del msg
        mensaje += "\n"
        # Codificar mensaje como arreglo de bytes
        mensaje = mensaje.encode()
        # Envío del mensaje codificado
        ser.write(mensaje)
        # Espera 1 segundo a que la mano se mueva
        time.sleep(1)
        # Cerrar el puerto serial
        ser.close()


    


