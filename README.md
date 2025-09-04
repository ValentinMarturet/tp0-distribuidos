# TP0: Docker + Comunicaciones + Concurrencia

### Ejercicio N°6:

Para agregar la funcionalidad de que los clientes puedan enviar batches de apuestas, no se requiere modificar demasiado el codigo.

Para el protocolo se creo una operacion nueva:
- BATCH = 4 
La cual es muy similar a la operacion APUESTA, pero le indica al servidor que hay mas apuestas en camino y que no tiene que cerrar el socket todavia.

Del lado del cliente, se leen las apuestas desde un archivo, el cual se accede a traves de una montura de volumen en docker:
```yaml
    volumes:
      - ./.data/agency-{i}.csv:/data/agency.csv
```

y se envian con el formato APUESTA1;APUESTA2;APUESTA3;APUESTA4;...;APUESTANN
Y se envian varios batches con un largo maximo.
El tamaño de los batches esta dado por el archivo de configuracion (batch: maxAmount).
Cuando se envia el utimo mensaje que contiene apuestas, se hace con la operación APUESTA, lo cual le indica al servidor que ya se enviaron todas las apuestas y puede cerrar la conexion.


Del lado del servidor, el servidor manda una confirmacion por cada batch recibido y confirma por logs cuando se recibieron todos los batches.