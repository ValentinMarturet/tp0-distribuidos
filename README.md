# TP0: Docker + Comunicaciones + Concurrencia

### Ejercicio N°5:

Para la comunicación entre el cliente y el servidor se creo un protocolo de comunicación simple, el cual consiste en:
    - 1 byte: código de operación (enum)
    - 4 bytes: longitud del mensaje (int, big endian)
    - N bytes: mensaje (string en UTF-8)

Los codigos de operacion posibles son:
    APUESTA = 1
    CONFIRMACION = 2
    ERROR = 3

Pero esto se puede ir expandiendo si es necesario en las proximas secciones.

En el campo mensaje se envia un string conteniendo el body del mensaje.
Se espera que los campos de las apuestas enviadas tengan el formato AGENCIA,NOMBRE,APELLIDO,DOCUMENTO,NACIMIENTO,NUMERO y que si se recibe mas de una apuesta en el mismo mensaje, esten separadas por `;`.

Para manejar los casos de short-reads y short-writes se implementaros funcion de read_exact y send_all. 
De esta forma se asegura que al escribir, se haya enviado todo el contenido que se deseaba enviar, y de no ser esto posible se retorna un error. Y que al leer, se haya leido todo el contenido esperado y si esto no se logra, se retorna un error.

