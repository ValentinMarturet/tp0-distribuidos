# TP0: Docker + Comunicaciones + Concurrencia

### Ejercicio N°1:

Se definio un script de bash `generar-compose.sh` para la creación de un Docker Compose con una cantidad de configurable de clientes. Se respeto el formato del archivo docker compose brindado por la catedra.

El script funciona llamando a otro script `generar-compose.py`, el cual escribe las lineas en un archivo con el nombre brindado, con la cantidad de clientes pedida. No se utilizaron librerias externas para la resolución

Correr el script con los siguientes parametros

```bash
./generar-compose.sh <nombre_archivo> <cantidad_clientes>
```