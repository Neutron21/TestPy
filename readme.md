# El env se encuentra dentro de la carpeta cursoFastApi
# El comando a ejecutar para activar el entorno virtual es:
    'source ivan-venv/bin/activate'
    'deactivate' para desactivar el venv

# Una vez activado el env se procede a correr el proyecto
# El cual se encuntra en la carpeta 'project', con el siguiente comando:
    'fastapi dev'
# Si el archivo main esta dentro de una carpeta se pone la ruta
    'fastapi dev app/main.py'

# En caso de ser un proyecto nuevo debemos instalar fastapi y standard con el siguiente comando
    'pip install "fastapi[standard]"'
# Para crear el entorno virutal se hace asi:
    'python3 -m venv' {{nombre del ambiente}} {{ruta}}
# La ruta es en caso de que no estemos en la carpeta donde queremos crear el entorno virtual
# El comando quedaria de la siguiente forma:
    'python3 -m venv ivan-venv cursoPython'
    
# Estructura del proyecto 
    cursoFastApi/
    │── app/
    │   │── __init__.py      # <- Asegúrate de que este archivo exista
    │   │── main.py          # <- Aquí se importa `models`
    │   │── models.py        # <- Debe estar en la misma carpeta que `main.py`
    │   │── routers/
    │── venv/                # <- Entorno virtual
    │── requirements.txt
    │── .env                 # <- No subir a Git

# Comando uvicorn, en ocasiones al agregar dependencias nuevas hay que recargar de nuevo el proyecto con uvicorn
# este debe hacerse con el venv activo y en la carpeta que contenga la carpeta app
