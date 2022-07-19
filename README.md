# Ant.fly

TP Final Base De Datos II - URL Shortener



## Authors

- [Martina Rodríguez](https://www.github.com/martirodriguez98)
- [Guido Gordyn Biello](https://www.github.com/ggordyn)
- [Ana Tarantino Pedrosa](https://www.github.com/anatarantino)



## Frontend

- Node.js
- Angular

### Instalación 

Compilar en la carpeta bitly/src utilizando:

```bash
  npm install
```

Luego para correr el frontend, en esa misma carpeta

```bash
  npm start
```

Se encontrará entonces corriendo en la url
http://localhost:4000


## Backend

- Python
- FastAPI
- PostgreSQL
- Redis

### Instalación 

Para instalar Redis
```bash
  docker pull redis
  docker run --name Myredis -p 6379:6379 -d redis
```
Redis estará corriendo en el puerto **6379**

Para instalar PostgreSQL
```bash
  docker pull postgres
  docker run -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres --name postgresql -p 5433:5432 -d postgres
```
Es importante que se deje el usuario **postgres** con contraseña **postgres**.

Luego crear la base antfly.  Para ello, una vez conectados a la misma, mediante CLI o un entorno gráfico, ejecutar el siguiente comando:

```bash
  CREATE DATABASE antfly 
```


Para ejecutar el backend se debe instalar Python3 y pipenv, luego correr el entorno virtual.
```bash
    sudo apt-get -y install pipenv
    pipenv shell
    pipenv install
```

Por último para ejecutar el backend, en la carpeta de backend/backend:

```bash
    uvicorn main:app --reload
```

La API correrá en http://localhost:8000.

Se puede consultar la documentación en Swagger en http://localhost:8000/docs en el navegador.



