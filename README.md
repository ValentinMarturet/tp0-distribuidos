# TP0: Docker + Comunicaciones + Concurrencia

### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `


Se creo un script `validar-echo-server.sh` el cual crea un nuevo container dentro de la network `tp0_testing_net` para que asi pueda testear el echo server utilizando `netcat`

#### Funcionamiento

Para que el script funcione correctamente, el servidor debe haber sido inicializado previamente, junto con la network `tp0_testing_net`.

El script crea un contenedor de docker a partir de la imagen `nicolaka/netshoot`, la cual contiene la dependencia `netcat` ya instalada y lo conecta a la network.

Una vez iniciado el container, corre dentro del mismo el comando `echo '$TEST_MESSAGE' | timeout $TIMEOUT nc $ECHO_SERVER_HOST $ECHO_SERVER_PORT 2>/dev/null` el cual envia `TEST_MESSAGE` al server en la direccion `ECHO_SERVER_HSOT` y el puerto `ECHO_SERVER_PORT`. `2>/dev/null` es para suprimir los errores.

Luego chequea si la respuesta es igual al mensaje enviado. 

En caso de exito, se logea `"action: test_echo_server | result: success"` y sino `"action: test_echo_server | result: fail"`

Por ultimo el script ejecuta un cleanup para remover el contenedor.

#### Ejecucion

Para correr el script realizar los siguientes comandos

```bash
./generar-compose.sh docker-compose-dev.yaml 1
make docker-compose-up
./validar-echo-server.sh
```