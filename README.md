# TP0: Docker + Comunicaciones + Concurrencia

### Ejercicio N°4:

Para implementar el graceful shutdown, se desarrolló un sistema de manejo de señales y banderas de control tanto en el cliente como en el servidor, permitiendo una terminación ordenada de los procesos.

El flujo principal se basa en tres componentes clave:
- Manejadores de señales: Interceptan las señales SIGTERM y SIGINT del sistema operativo
- Bandera de control: Una variable booleana (running) que coordina el estado del proceso
- Proceso de limpieza: Cierre ordenado de recursos y conexiones

Cuando el sistema recibe una señal de terminación:

- Captura de señal: Los manejadores detectan SIGTERM o SIGINT
- Activación del shutdown: Se establece running = false y se inicia el proceso de cierre
- Cierre de conexiones: Se cierran todos los sockets activos para interrumpir operaciones bloqueantes
- Salida del loop principal: Los procesos verifican la bandera y terminan sus ciclos de ejecución
- Limpieza final: Se ejecuta el cleanup de recursos restantes