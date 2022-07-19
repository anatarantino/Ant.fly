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
- PostreSQL
- Redis

### Instalación 

Descargar y correr las imágenes provistas por la cátedra de Redis y PostgreSQL.

Asignar a Redis el puerto **6379** y a PostgreSQL el puerto **5433**.

Crear el usuario postgres con contraseña postgres para esta última, y crear la base bitly.

```bash
  CREATE DATABASE bitly 
```


Para ejecutar el backend se debe instalar Python3 y pipenv, luego correr el entorno virtual.
```bash
    sudo apt-get -y install pipenv
    pipenv shell
    pipenv install
```

Por último para ejecutar el backend, en la carpeta de backend:

```bash
    uvicorn main:app --reload
```

La API correrá en http://localhost:8000.

Se puede consultar la documentación en Swagger en http://localhost:8000/docs en el navegador.



