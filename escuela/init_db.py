from app import app
from app.extensions import db
# Importamos todos tus modelos para que SQLAlchemy los reconozca en memoria
from app.models import Curso, Docente, Estudiante, Materia, Nota, Asistencia

with app.app_context():
    # Extraemos el metadata cargado de tus modelos (todos comparten el mismo metadata)
    metadata = Curso.metadata

    print("Se crearan las tablas:")
    for tabla in metadata.sorted_tables:
        print("->", tabla.name)

    # Creamos las tablas en la base de datos MySQL
    metadata.create_all(bind=db.engine)

    print("Creado correctamente")