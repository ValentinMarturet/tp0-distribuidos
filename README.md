# TP0: Docker + Comunicaciones + Concurrencia


### Ejercicio N°2:

Para lograr esto, se agregaron monturas de volumenes dentro del template de docker compose provisto por la catedra, para que los contenedores peudan acceder a los archivos de configuración actualziados sin necesidad de reconstruir la imagen.

Servidor:
```yaml
    volumes:
      - ./server/config.ini:/config.ini
```

Cliente:
```yaml
    volumes:
      - ./client/config.yaml:/config.yaml
```

Tambien se quitaron las variables de entorno provistas en el compose, para que tanto el servidor como el cliente utilicen los valores obtenidos de los archivos de configuración.