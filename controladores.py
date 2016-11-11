"""
Este script contiene los siguientes controladores 
(pensados para la mano de 3 dedos del lab)

- Ctrl_ERC: Controlador principal, basado en el paper de EnRoCo.
    Uso: dedo índice y/o anular.

- Ctrl_Pulgar: Controlador en construcción, estructura "similar"
        al controlador Ctrl_ERC.
    Uso: dedo pulgar.

"""
# Importación de módulos
import mis_funciones as mf
import numpy as np
import time


# CLASE 1

class Ctrl_ERC():
    """Modelado de controlador basado en EnRoCo. Para usarse
        con dedo índice y/o anular."""

    def __init__(self,
            dedo="indice", 
            cantidad_motores=2,
            tercer_servo_auto=False,
            # Si se ven dos verdes, hay que dividir la imagen
            yema_pulgar_visible=False,
            ):
        """Inicialización del controlador"""
        # Para 2 o 3 motores por dedo
        # if (cantidad_motores != 2) and (cantidad_motores != 3):
            # print(" ")
            # print("------------------------------------------")
            # print("[ERROR] Implementación para 2 o 3 motores!")
            # print("------------------------------------------")
            # print(" ")

        # Yema del pulgar visible <=> el pulgar está hacia arriba
        self.yema_pulgar_visible = yema_pulgar_visible

        # Tercer servo automático (apunta siempre a la misma dirección)
        if cantidad_motores == 3:
            self.tercer_servo_auto = False
        else:
            self.tercer_servo_auto = tercer_servo_auto

        # ==========================================================
        # Se debe diferenciar según que dedo se controle 
        # (color yema y codificación primer servo)
        self.dedo = dedo

        # ==========================================================
        # Para convertir de número codificado a ángulo y viceversa
        self.m_n2a_s2 = 300/1024
        self.n_n2a = -150

        if self.dedo == "indice":
            self.m_n2a_s1 = 300/4096
        elif self.dedo == "anular":
            self.m_n2a_s1 = self.m_n2a_s2 

        # ==========================================================
        # Un arreglo de primitivas (diccionarios)
        self.primitivas = []

        # Un diccionario de "flags" para control de flujo
        self.flags = {
                "_explorar_": False,   # Este es un explorar de un paso
                "_acercando_": False,
                "_alejando_": False,
                "_alcanzado_": False,
                "_nueva_primitiva_": False,
                "_primera_exploracion_": True,
                }

        # Cantidad de motores
        self.cantidad_motores = cantidad_motores

        # Posiciones límite de cada servo se copian de los 
        # atributos de la mano
        if dedo == "indice":
            self.limites = np.array([[200, 200, 200], [2100, 550, 550]])

        elif dedo == "anular":
            self.limites = np.array([[200, 200, 200], [550, 550, 513]])
            
        elif dedo == "pulgar":
            self.limites = np.array([[825, 200, 200], [2350, 513, 513]])

        # Asociar el color de la yema
        if dedo == "indice" or dedo == "pulgar":
            # yemas en indice y pulgar son verdes
            self.color = "green"
            # El primer servo es un "mx" (2048 niveles)
            self.primer_servo = "mx"

        # Sólo queda la opción de que sea el dedo anular
        else:
            self.color = "blue"
            # El primer servo es un "ax" (1024 niveles)
            self.primer_servo = "ax"


    def explorar(self, camara, mano):
        """Metodo de exploración, genera primitivas aleatorias"""
        print("\n\tExplorando...")
        # pasos: cantidad de movimientos de exploración, la idea
        # es que sea igual a la cantidad de motores (ortogonalidad)

        if self.flags["_primera_exploracion_"]:
            pasos = self.cantidad_motores
            
        else: 
            pasos = 1

        # Matriz identidad (una fila, una primitiva)
        identidad = np.identity(pasos, dtype="int64")
        # Generación de cada primitiva
        for paso in range(0, pasos):

            print("\t-> generando primitiva")
            # temp: temporal, nueva primitiva de exploración
            temp = {}
            temp["exploracion"] = True
            # Obtener posición yema
            ri = mano.actualizar_yema(camara, self.dedo)

            # La posición inicial de esta primitiva
            temp["pos_inicial"] = ri

            # La parte aleatoria (entero entre 15 y 30)
            aleatorio = np.random.randint(20, 41)
        
            # Magnitud (vector) de una primitiva
            magnitud = aleatorio * identidad[paso, :]
            # Si el primer_servo es mx, aumentar la magnitud
            if paso == 0 and self.primer_servo == "mx":
                magnitud *= 4    
            # Signo aleatorio 
            signo = np.random.randint(0, 2)
            if signo == 0:
                magnitud *= -1
            # La magnitud de la primitiva
            temp["magnitud"] = magnitud
             
            # Ahora se debe mover el dedo correspondiente
            # Obtener posición actual
            dedo_pos = mano.entregar_dedo_pos(dedo=self.dedo) 
            # Modificar con la primitiva temporal
            if len(magnitud) == 2:
                magnitud = np.concatenate([magnitud, [0]])

            dedo_pos += magnitud
            # ENTREGA FLAG PARA ADVERTIR LIMITACION DE ANGULO
            limitado, _, _ = mano.ajustar_dedo(self.dedo, dedo_pos)
            temp["limitado"] = limitado

            # ================================================== # 
            # Calcular el tercer servo automáticamente
            if self.tercer_servo_auto:
                
                # Servos 1 y 2 codificados
                dedo_pos = mano.entregar_dedo_pos(self.dedo)
                primer_servo = dedo_pos[0]
                segundo_servo = dedo_pos[1]

                # Servos 1 y 2 en ángulos (0~360°)
                primer_servo = -(primer_servo*self.m_n2a_s1 + self.n_n2a)
                segundo_servo = -(segundo_servo*self.m_n2a_s2 + self.n_n2a)

                # Servo 3 en ángulo y luego a codificado
                tercer_servo = 170 - (primer_servo + segundo_servo)
                tercer_servo = (150 - tercer_servo)/self.m_n2a_s2
                
                # Agregando el ángulo ajustado del servo 3
                dedo_pos[-1] = int(tercer_servo)
                _ = mano.ajustar_dedo(self.dedo, dedo_pos)
            
            # ================================================== #

            # Mover dedo (la espera de 1 segundo está incluída)
            mano.mover()
    
            # Obtener posición yema
            rf = mano.actualizar_yema(camara, self.dedo)

            temp["pos_final"] = rf
            # Diferencia (movimiento yema en la imagen)
            diferencia = rf - ri
            temp["diferencia"] = diferencia

            # Agregar a la lista de primitivas del controlador
            self.primitivas.append(temp)
            # Elimina temp (para reutilizarlo en la sig. iteración)
            del temp
        # Fin del método
        

    def calcular_primitiva(self, r_objetivo, camara, mano):
        """Calcula una nueva primitiva a partir de las existentes"""
        print("\n\tCalculando primitiva...\n")
        # Devuelve flag booleano SINGULAR
        singular = False
        # Se debe hacer una lista de distancias, para lo que se
        # necesita la posición actual de la yema y la lista de 
        # primitivas creadas

        # Obtener posición yema
        r = mano.actualizar_yema(camara, self.dedo)

        # Copia de la lista de primitivas
        primitivas = self.primitivas[:]
        # Se debe calcular la distancia entre cada primitiva y r
        distancias = []
        infinito = float("inf")
        for primitiva in primitivas:
            # No considerar aquellas que producen flag "limitado"
            if primitiva["limitado"] == True:
                distancias.append(infinito)
            else:
                dist = np.linalg.norm(primitiva["pos_inicial"] - r)
                distancias.append(dist)

        # Ahora que se tiene la lista de distancias
        # hay que encontrar las primitivas más cercanas
        indices_sort = np.argsort(distancias)
        # print("[DEBUG] Length distancias: {}".format(len(distancias)))
        # print("[DEBUG] Distancias: {}".format(distancias))


        dim = self.cantidad_motores
        # Matriz de magnitudes y diferencias
        magnitudes = np.zeros([dim, dim])
        diferencias = np.zeros([2, dim])
        for i in range(0, dim):
            temp = primitivas[indices_sort[i]]["magnitud"]
            # print("[DEBUG] Temp magnitud: {}".format(temp))
            magnitudes[:, i] = np.reshape(temp, (1, dim))
            # print("[DEBUG] Magnitudes: {}".format(magnitudes))
            
            temp = primitivas[indices_sort[i]]["diferencia"]
            # print("[DEBUG] Temp diferencia: {}".format(temp))
            diferencias[:, i] = np.reshape(temp, (1, 2))
            # print("[DEBUG] Diferencias: {}".format(diferencias))

        # Matriz de pesos (ponderaciones por cercanía)
        # (hasta 5 motores)
        w_a = np.ones((1, 5))
        w_b = np.arange(0, 1, 0.2)
        w_c = w_a - w_b
        # Aquí se arma la matriz (diagonal)
        w = np.diag(w_c[0, :dim])

        # Vector de desplazamiento requerido (en imagen)
        b2 = r_objetivo - r
        # Como vector columna...
        b2 = b2.reshape([2, 1])
        
        # ---------------------------------------------------
        # ---------------------------------------------------
        # EL PROGRAMA SE CAE AL CALCULAR EL DETERMINATE DE A, 
        # YA QUE NO ES UNA MATRIZ CUADRADA. SE PUEDE ESTIMAR
        # X CON EL ESTIMADOR DE MINIMOS CUADRADOS (ESPI)
        # Ax=b  ->  x = (A'A)^-1A'b    
        # ---------------------------------------------------
        # ---------------------------------------------------
        # A2*W*x = b2  A2 es la matriz de diferencias
        A = np.dot(diferencias, w)
        
        
        # Si no se puede resolver el sistema Ax = b2...
        # if np.linalg.det(A) == 0:
            # print("\n\t\tMatriz singular! => Explorar\n")
            # singular = True
            # return
        # Ponderaciones de primitivas anteriores
        # No se puede resover directamente, ya que la matriz A no 
        # queda cuadrada al controlar 3 motores (2x3)
        # x = np.linalg.solve(A, b2)

        try:
            # print("[DEBUG] A: {}".format(A))
            # print("[DEBUG] b2: {}".format(b2))
            # print("[DEBUG] Shape A: {}".format(A.shape))
            # print("[DEBUG] Shape b2: {}".format(b2.shape))
            x = np.linalg.inv(A.T.dot(A)).dot(A.T).dot(b2) 

        except np.linalg.linalg.LinAlgError:
            # Todos los flags a False excepto el flag _explorar_
            for key in self.flags.keys():
                self.flags[key] = False
            self.flags["_explorar_"] = True

            print("\n---------------------------------------------------------------")
            msg = "\t[Error] No se pudo resolver el sistema de ecuaciones"
            print(msg)
            print(" ")
            print("[DEBUG] A: {}".format(A))
            print("[DEBUG] b2: {}".format(b2))
            print("[DEBUG] Shape A: {}".format(A.shape))
            print("[DEBUG] Shape b2: {}".format(b2.shape))
            print("---------------------------------------------------------------\n")
            singular = True
            return singular
        else:
            # print("[DEBUG] x (ponderaciones): {}".format(x))

            # A1*W*x = b1    A1 es matriz de magnitudes, b1 es magnitud
            # de la nueva primitiva
            A = np.dot(magnitudes, w)
            b1 = np.dot(A, x).astype("int64")

            # Ahora se debe mover el dedo correspondiente
            # Obtener posición actual
            dedo_pos = mano.entregar_dedo_pos(dedo=self.dedo) 
            # Modificar con la nueva primitiva 
            # print("[DEBUG] dedo_pos: {}".format(dedo_pos))
            # print("[DEBUG] b1: {}".format(b1))

            # En caso de que se controlen 2 motores
            # (se deja libre el de la yema)
            if len(b1) == 2:
                b1 = b1.reshape(1, 2)[0]
                b1 = np.concatenate([b1, [0]])
                # Cuando se guarde b1, no se considerará el 
                # 0 que se concatenó recién
                flag_b1_dim_2 = True

            elif len(b1) == 3:
                b1 = b1.reshape(1, 3)[0]
                flag_b1_dim_2 = False

            # Las primitivas genereadas son muy grandes
            # en magnitud y produce movimientos muy grandes
            norma_b1 = np.linalg.norm(b1)
            param_limitacion = 150
            if norma_b1 > param_limitacion:
                b1 = param_limitacion*(b1/norma_b1)
                b1 = b1.astype("int64")

            # print("[DEBUG] dedo_pos: {}".format(dedo_pos))
            # print("[DEBUG] b1: {}".format(b1))

            # ===============================================
            # Manejo de servos limitados
            # ===============================================
            # Si es que el servo está limitado y se quiere
            # seguir moviendo...
            # Si el primer servo está al límite (inferior)
            if dedo_pos[0]==self.limites[0, 0] and b1[0]<0:
                # El otro servo se puede mover y lo iba a 
                # hacer en la misma dirección?
                if dedo_pos[1]!=self.limites[0, 1] and b1[1]<0: 
                    if abs(b1[0])>abs(b1[1]):
                        b1[1] = b1[0]
                        b1[0] = 0
                    else:
                        b1[0] = 0
                        # b1[1] se mantiene

            # Si el primer servo está al límite (superior)
            if dedo_pos[0]==self.limites[1, 0] and b1[0]>0:
                # El otro servo se puede mover y lo iba a 
                # hacer en la misma dirección?
                if dedo_pos[1]!=self.limites[1, 1] and b1[1]>0: 
                    if b1[0]>b1[1]:
                        b1[1] = b1[0]
                        b1[0] = 0
                    else:
                        b1[0] = 0
                        # b1[1] se mantiene

            # Si el segundo servo está al límite (inferior)
            if dedo_pos[1]==self.limites[0, 1] and b1[1]<0:
                # El otro servo se puede mover y lo iba a 
                # hacer en la misma dirección?
                if dedo_pos[0]!=self.limites[0, 0] and b1[0]<0: 
                    if abs(b1[0])<abs(b1[1]):
                        b1[0] = b1[1]
                        b1[1] = 0
                    else:
                        b1[1] = 0
                        # b1[1] se mantiene

            # Si el segundo servo está al límite (superior)
            if dedo_pos[1]==self.limites[1, 1] and b1[1]>0:
                # El otro servo se puede mover y lo iba a 
                # hacer en la misma dirección?
                if dedo_pos[0]!=self.limites[1, 0] and b1[0]>0: 
                    if b1[0]<b1[1]:
                        b1[0] = b1[1]
                        b1[1] = 0
                    else:
                        b1[1] = 0
                        # b1[1] se mantiene

            # ===============================================

            dedo_pos += b1

            # Se comienza a crear una nueva primitiva (diccionario)
            nueva_primitiva = {}
            if flag_b1_dim_2:
                nueva_primitiva["magnitud"] = b1[:-1]
            else:
                nueva_primitiva["magnitud"] = b1

            # ENTREGA FLAG PARA ADVERTIR LIMITACION DE ANGULO
            limitado, _, _ = mano.ajustar_dedo(self.dedo, dedo_pos)
            nueva_primitiva["limitado"] = limitado
            
            
            # ================================================== # 
            # Calcular el tercer servo automáticamente
            if self.tercer_servo_auto:
                
                # Servos 1 y 2 codificados
                dedo_pos = mano.entregar_dedo_pos(self.dedo)
                primer_servo = dedo_pos[0]
                segundo_servo = dedo_pos[1]

                # Servos 1 y 2 en ángulos (0~360°)
                primer_servo = -(primer_servo*self.m_n2a_s1 + self.n_n2a)
                segundo_servo = -(segundo_servo*self.m_n2a_s2 + self.n_n2a)

                # Servo 3 en ángulo y luego a codificado
                tercer_servo = 170 - (primer_servo + segundo_servo)
                tercer_servo = (150 - tercer_servo)/self.m_n2a_s2
                
                # Agregando el ángulo ajustado del servo 3
                dedo_pos[-1] = int(tercer_servo)
                _, _, _ = mano.ajustar_dedo(self.dedo, dedo_pos)
            
            # ================================================== #
           
           
            # Mover dedo (la espera de 1 segundo está incluída)
            mano.mover()

            # Obtener posición yema (posición final)
            rf = mano.actualizar_yema(camara, self.dedo)

            nueva_primitiva["pos_final"] = rf

            # Diferencia (movimiento yema en la imagen)
            diferencia = rf - r
            nueva_primitiva["diferencia"] = diferencia

            nueva_primitiva["exploracion"] = False
            nueva_primitiva["pos_inicial"] = r


            # Agregar a la lista de primitivas del controlador
            self.primitivas.append(nueva_primitiva)
            # Fin del método
        return singular


    def evaluar_estado(self, r_objetivo):
        """Evalúa el estado de la mano y actualiza flags 
            de control de flujo """
        # La primitiva más reciente
        primitiva = self.primitivas[-1]
        # print("[DEBUG] P. mas reciente: {}".format(primitiva))
        print("[DEBUG] Magnitud: {}".format(primitiva["magnitud"]))

        # Posición inicial y final
        pos_inicial = primitiva["pos_inicial"]
        pos_final = primitiva["pos_final"]
        
        # Distancia al objetivo antes y después
        dif_antes = pos_inicial - r_objetivo 
        dif_despues = pos_final - r_objetivo 

        dist_antes = np.linalg.norm(dif_antes)
        dist_despues = np.linalg.norm(dif_despues)

        # Distancia mínima para considerar objetivo alcanzado (pixeles)
        # dist_minima = 20
        dist_minima = 10

        estado = None
        if dist_despues < dist_minima:
            # el objetivo se alcanzó
            estado = "alcanzado"

        elif dist_despues < dist_antes:
            # Se acerca al objetivo
            estado = "acercando"

        else:
            # Se aleja del objetivo
            estado = "alejando"

        #####################################
        if estado == "alcanzado":
            self.flags["_explorar_"] = False            
            self.flags["_acercando_"] = False           
            self.flags["_alejando_"] = False            
            self.flags["_alcanzado_"] = True           
            self.flags["_nueva__primitiva_"] = False    

        elif estado == "acercando":
            self.flags["_explorar_"] = False            
            self.flags["_acercando_"] = True           
            self.flags["_alejando_"] = False            
            self.flags["_alcanzado_"] = False           
            self.flags["_nueva__primitiva_"] = True    

        elif estado == "alejando":
            self.flags["_explorar_"] = True            
            self.flags["_acercando_"] = False           
            self.flags["_alejando_"] = True            
            self.flags["_alcanzado_"] = False           
            self.flags["_nueva__primitiva_"] = False    
        
        return estado 


    def ajuste_fino(self, camara, mano):
        """Para mover los dedos luego de que se considere
        alcanzado el objetivo (en primera instancia). Esta
        función asegura el contacto entre yema y objeto."""
        # Caso índice: sólo mover servo 1, cerrándose (restando)

        while True:
            # Hay contacto yema-objeto?
            imagen = mf.take_picture(camara)
            contacto, dist = mf.hay_contacto(imagen, self.dedo)

            # Si se alcanza el objetivo, termina
            if contacto:
                print("Objetivo alcanzado por dedo {}".format(self.dedo))
                break

            if dist > 7:
                # Un aumento de x grados se logra con -x/m 
                grados = 3

            else:
                # Un aumento de x grados se logra con -x/m 
                grados = 1

            print("[DEBUG] {} grados más...".format(grados))

            # Posición actual del dedo
            dedo_pos = mano.entregar_dedo_pos(self.dedo) 

            # Actualización servo 1
            magnitud = -grados/self.m_n2a_s1
            dedo_pos[0] += int(magnitud)

            # Compensación tercer servo
            magnitud = grados/self.m_n2a_s2
            dedo_pos[2] += int(magnitud)
            
            # Ajuste y movimiento
            _, _, _ = mano.ajustar_dedo(self.dedo, dedo_pos)
            mano.mover()

        # Un último movimiento (de 1°)
        magnitud = -1/self.m_n2a_s1
        dedo_pos = mano.entregar_dedo_pos(self.dedo) 
        dedo_pos[0] += int(magnitud)
        _, _, _ = mano.ajustar_dedo(self.dedo, dedo_pos)
        mano.mover()


    def cargar_primitivas(self):
        """Función que permite usar primitivas generadas
        anteriormente."""
        # Hacer esta función xD


# CLASE 2


class Ctrl_Pulgar():
    """Un controlador simple para el dedo pulgar"""

    def __init__(self, primitivas=None):
        """Inicialización del controlador."""
        
        # La lista de primitivas
        if primitivas != None:
            self.primitivas = primitivas

        else:
            self.primitivas = []

        # Conversión de grados a ángulo (válido para servos "ax")
        self.m_n2a = 300/1024
        self.n_n2a = -150


    def explorar_ex(self, camara, mano):
        """Mueve el dedo y guarda información sobre el cambio
            producido en la imagen."""
        # Exploración "Exhaustiva"
        # Donde estaba el dedo, antes de comenzar
        dedo_inicial = mano.entregar_dedo_pos("pulgar").copy()

        # Mueve el servo, haciendo que se cierre, siempre desde la
        # posición inicial.
        # ~90°: pos inicial
        # 80°: primer movimiento
        # 70°: segundo movimiento
        # etc...
        angulos = list(range(0, 81, 10))
        angulos.reverse()
        for angulo in angulos:
            # "Primitiva" temporal:
            temp = {}

            # Pos_inicial de la yema en la imagen
            ri = mano.actualizar_yema(camara, "pulgar")
            temp["pos_inicial"] = ri

            # Posición actual del dedo
            dedo_pos = mano.entregar_dedo_pos("pulgar").copy()

            # Hay que considerar la altura del dedo (servo 1)
            temp["servo_1"] = dedo_pos[0].tolist()

            # El segundo servo se ajusta para el ángulo dado
            segundo_servo = int((150 - angulo)/self.m_n2a)

            # Magnitud de la primitiva/ajuste del servo
            temp["magnitud"] = segundo_servo - dedo_pos[1]

            dedo_pos[1] = segundo_servo
            _ = mano.ajustar_dedo("pulgar", dedo_pos)

            #============================================
            # Ajuste automático del tercer servo
            # Ángulos de servos 2  y 3 (0~360°)
            servo_2_ang = -(dedo_pos[1]*self.m_n2a + self.n_n2a)
            servo_3_ang = 90 - servo_2_ang 
            
            # Ángulo servo 3 (codificado)
            servo_3_cod = (150 - servo_3_ang)/self.m_n2a
            dedo_pos[2] = servo_3_cod
            _ = mano.ajustar_dedo("pulgar", dedo_pos)
            #============================================

            mano.mover()
            time.sleep(1)

            # Pos_final de la yema en la imagen
            rf = mano.actualizar_yema(camara, "pulgar")
            temp["pos_final"] = rf
            temp["diferencia"] = rf - ri

            # Guardar la información generada
            self.primitivas.append(temp)

            # Borrar evita que se sobreescriban las primitivas
            del temp

            # Para terminar, devolver el dedo a donde estaba
            _ = mano.ajustar_dedo("pulgar", dedo_inicial)
            mano.mover()
            time.sleep(1)

        # DEBUG
        print(" ")
        print(self.primitivas)
        print(" ")


    def mover(self, punto_objetivo, camara, mano):
        """Mueve el dedo al punto especificado. Consiste de un 
            solo movimiento. Luego se debe llamar a "ajuste_fino"."""
        
        # Posición actual de la yema en la imagen
        ri = mano.actualizar_yema(camara, "pulgar")

        # Buscar la primitiva más cercana 
        primitivas = self.primitivas[:]
        
        # Distancias entre primitivas (pos_final) y punto objetivo
        distancias = []
        
        for primitiva in primitivas:
            dist = np.linalg.norm(np.array(primitiva["pos_final"]) - np.array(punto_objetivo))
            distancias.append(dist)

        # Indices que ordenan en función de la más cercana
        indices_sort = np.argsort(distancias)

        # La primitiva más cercana y el cambio que produjo en imagen
        primitiva = primitivas[indices_sort[0]]
        delta_primitiva = primitiva["diferencia"][0]

        # El cambio que quiero producir en la imagen (horizontal)
        delta_buscado = punto_objetivo[0] - ri[0]

        # Ponderador x
        x = delta_buscado/delta_primitiva

        # Ponderación de la magnitud de la primitiva
        magnitud = x * primitiva["magnitud"]

        # Movimiento...
        dedo_pos = mano.entregar_dedo_pos("pulgar")
        dedo_pos[1] += magnitud
            
        #============================================
        # Ajuste automático del tercer servo
        # Ángulos de servos 2  y 3 (0~360°)
        servo_2_ang = -(dedo_pos[1]*self.m_n2a + self.n_n2a)
        servo_3_ang = 90 - servo_2_ang 
        
        # Ángulo servo 3 (codificado)
        servo_3_cod = (150 - servo_3_ang)/self.m_n2a
        dedo_pos[2] = servo_3_cod
        _ = mano.ajustar_dedo("pulgar", dedo_pos)
        #============================================

        mano.mover()


    def evaluar_estado(self):
        """Evalúa si el movimiento realizado cumplió con su objetivo
            o si se necesita seguir moviendo"""
        pass


    def ajuste_fino(self, camara, mano):
        """Mueve el segundo servo del dedo en saltos de 1 o 3 grados
            hasta que haya contacto entre la yema y el objeto."""
        # Caso pulgar: sólo mover servo 2, cerrándose (sumando)

        while True:
            # Hay contacto yema-objeto?
            imagen = mf.take_picture(camara)
            contacto, dist = mf.hay_contacto(imagen, "pulgar", 
                                            kernel=[5,7])

            # Si se alcanza el objetivo, termina
            if contacto or (dist < 7):
                print("Objetivo alcanzado por dedo pulgar")
                break

            else:
                # Un aumento de x grados se logra con -x/m 
                grados = 1

            print("[DEBUG] {} grados más...".format(grados))

            # Posición actual del dedo
            dedo_pos = mano.entregar_dedo_pos("pulgar") 

            # Actualización servo 2
            magnitud = grados/self.m_n2a
            dedo_pos[1] += int(magnitud)

            # Compensación servo 3
            magnitud = -grados/self.m_n2a
            dedo_pos[2] += int(magnitud)
            
            # Ajuste y movimiento
            _, _, _ = mano.ajustar_dedo("pulgar", dedo_pos)
            mano.mover()

        # Un último movimiento (de 1°)
        magnitud = 1/self.m_n2a
        dedo_pos = mano.entregar_dedo_pos("pulgar") 
        dedo_pos[1] += int(magnitud)
        _, _, _ = mano.ajustar_dedo("pulgar", dedo_pos)
        mano.mover()






