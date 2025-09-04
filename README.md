# TP0: Docker + Comunicaciones + Concurrencia

### Ejercicio N°7:


#### Operaciones del Protocolo

Se incorporan nuevas operaciones al protocolo, quedando definido de la siguiente manera:

- `APUESTA = 1`  
- `CONFIRMACION = 2`  
- `ERROR = 3`  
- `BATCH = 4`  
- `WINNERS = 5`  
- `NOT_READY = 6`  
- `READY = 7`  

> Nota: la operación `APUESTA` ya no tiene utilidad en este sistema.

---

## Flujo de Interacción

1. **Finalización de apuestas**  
   - Cuando un cliente envía todas sus apuestas, envía un mensaje al servidor con su **ID de agencia** y la operación `READY`.

2. **Solicitud de ganadores**  
   - Inmediatamente después, el cliente abre **otro socket** y envía al servidor un mensaje con su **ID de agencia** y la operación `WINNERS`.  
   - El cliente espera dos posibles respuestas:
     - **`NOT_READY`**: si el servidor todavía no realizó el sorteo (porque falta alguna agencia).  
       En este caso, el cliente deberá esperar un tiempo y volver a enviar la petición `WINNERS`.  
     - **`WINNERS`**: si el sorteo ya fue realizado, el servidor responde con una string en el body del mensaje, conteniendo los **DNIs ganadores de esa agencia** separados por comas (`,`).  

---

#### Clase `Lottery`

Del lado del servidor se implementa la clase `Lottery`, que se encarga de:

- Registrar qué agencias ya enviaron todas sus apuestas (`READY`).  
- Realizar el sorteo cuando todas las agencias notificaron.  

El flujo es el siguiente:

1. A medida que el servidor recibe mensajes `READY`, se lo informa a `Lottery`.  
2. Cuando las 5 agencias notificaron, `Lottery` ejecuta el sorteo.  
3. Si un cliente consulta ganadores (`WINNERS`) **antes** del sorteo, el servidor responde con `NOT_READY`.  
4. Si consulta **después**, el servidor responde con la lista de DNIs ganadores de su agencia.  
