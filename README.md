# TP0: Docker + Comunicaciones + Concurrencia

## Ejercicio N°8

Debido a la simpleza del servidor y lo controlado del sistema, se decidió manejar la concurrencia utilizando **threads**, en lugar de opciones más complejas como **threadpools**, para gestionar las múltiples conexiones.  
Esto bajo el supuesto de que el servidor no será objeto de ataques de múltiples conexiones destinadas a saturar los threads.  
De todas formas, se estableció un número máximo de conexiones simultáneas permitido.

El funcionamiento es el siguiente:

- El servidor corre en un **thread principal**, encargado de aceptar las conexiones entrantes de los clientes.  
- Si se supera el número máximo de conexiones simultáneas, el servidor responde inmediatamente al cliente con un **mensaje de error**, indicando que se alcanzó el límite de conexiones.  
- Si no se supera dicho número, el servidor levanta un **nuevo thread** para manejar la conexión.  

---

## Locks utilizados

Para coordinar el acceso a recursos compartidos se implementaron **locks**:

- **Lock para el objeto `Lottery`**:  
  Su estado solo debe ser modificado por un thread a la vez.  

- **Lock para el acceso a las apuestas**:  
  Este lock se utiliza cada vez que se quiere guardar u obtener apuestas.  
  Dado que no se pueden modificar directamente las funciones de `utils.py`, el servidor aplica este lock al interactuar con:  
  - `load_bets()`  
  - `store_bets()`  

  Con esto se garantiza que solo un hilo acceda a los archivos de almacenamiento a la vez.

> **Nota:** El lock de acceso a apuestas podría implementarse como un **lock de lectura-escritura (RWLock)**, ya que no es necesario bloquear dos hilos que únicamente desean leer el archivo de manera simultánea.  
> Sin embargo, con la implementación actual no hay impacto negativo, ya que la única lectura se realiza desde la clase `Lottery`, y solo una vez, al momento de ejecutar el sorteo.

---

## Consideración sobre el GIL

La consigna indica tener en cuenta el **GIL (Global Interpreter Lock)** de Python.  

Analizando el caso:  
- El GIL asegura que **dos hilos no puedan ejecutar bytecode de Python en simultáneo**.  
- Esto sería un gran problema si las operaciones fueran intensivas en CPU.  
- En este trabajo, las operaciones son principalmente de **entrada/salida (I/O)**, por lo que el impacto del GIL es mínimo y no afecta de manera considerable al desempeño del servidor.
