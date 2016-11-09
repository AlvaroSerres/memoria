# memoria
Todo el código relativo al control de la mano de 3 dedos

*OBS: El contenido actual del branch master no es una versión definitiva.

Los programas que comienzan con "0" son programas para probar 
que se pueda mover la mano, que el controlador funcione y que
el filtrado por color este funcionando según las condiciones
de luz del momento.

Los programas que comienzan con "1" son programas en que se implementaron
ciertos algoritmos que ahora se encuentran en el script "mis_funciones.py"

De lo que queda: 

>  "controladores.py" (antiguamente llamado "controlador.py")
    almacena las clases de controladores. Actualmente hay un controlador 
    para el dedo índice/anular y, en etapa de desarrollo, un controlador
    para el dedo pulgar.
    
>  "mis_funciones.py" almacena funciones útiles (escritas por mi), principalmente
    en cuanto a procesamiento de imagen/visión. Aquí también está la clase
    mano, en donde se intenta modelar la mano completa.
    
>  "main_indice.py" es un programa que controla el dedo índice, haciéndolo llegar
    a un punto objetivo (definido por el contacto con el contorno de un objeto ROJO).
    Se está usando una etapa de exploración previa, la cual será reemplazada por 
    un proceso de carga de primitivas guardadas con anterioridad (modulo JSON de Python).
    
>  "main_pulgar.py" es un programa en desarrollo. Controlará únicamente el dedo
    pulgar para que puede llegar a hacer contacto con el objeto (de color ROJO).
