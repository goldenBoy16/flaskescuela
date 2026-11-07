from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship


class Curso(Model):
    __tablename__ = "curso"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)       # ej. "3.° Secundaria"
    paralelo = Column(String(5), nullable=False)      # A, B...
    gestion = Column(Integer, nullable=False)         # año lectivo

    # Relaciones inversas (uno a muchos)
    estudiantes = relationship("Estudiante", back_populates="curso", cascade="all, delete-orphan")
    materias = relationship("Materia", back_populates="curso", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.nombre} '{self.paralelo}' ({self.gestion})"


class Docente(Model):
    __tablename__ = "docente"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    especialidad = Column(String(80))
    telefono = Column(String(20))
    email = Column(String(120))

    # Relación inversa
    materias = relationship("Materia", back_populates="docente")

    def __repr__(self):
        return self.nombre


class Estudiante(Model):
    __tablename__ = "estudiante"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    ci = Column(String(20), unique=True, nullable=False)
    fecha_nacimiento = Column(Date)
    tutor = Column(String(100))
    telefono_tutor = Column(String(20))
    
    curso_id = Column(Integer, ForeignKey("curso.id"), nullable=False)
    curso = relationship("Curso", back_populates="estudiantes")

    # Relaciones inversas
    notas = relationship("Nota", back_populates="estudiante", cascade="all, delete-orphan")
    asistencias = relationship("Asistencia", back_populates="estudiante", cascade="all, delete-orphan")

    def __repr__(self):
        return self.nombre


class Materia(Model):
    __tablename__ = "materia"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    horas_semanales = Column(Integer, default=4)
    
    curso_id = Column(Integer, ForeignKey("curso.id"), nullable=False)
    curso = relationship("Curso", back_populates="materias")
    
    docente_id = Column(Integer, ForeignKey("docente.id"), nullable=False)
    docente = relationship("Docente", back_populates="materias")

    # Relaciones inversas
    notas = relationship("Nota", back_populates="materia", cascade="all, delete-orphan")
    asistencias = relationship("Asistencia", back_populates="materia", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.nombre} - {self.curso}"


class Nota(Model):
    __tablename__ = "nota"
    id = Column(Integer, primary_key=True)
    trimestre = Column(Integer, nullable=False)       # 1, 2, 3
    calificacion = Column(Float, nullable=False)      # 0 a 100
    
    estudiante_id = Column(Integer, ForeignKey("estudiante.id", ondelete="CASCADE"), nullable=False)
    estudiante = relationship("Estudiante", back_populates="notas")
    
    materia_id = Column(Integer, ForeignKey("materia.id", ondelete="CASCADE"), nullable=False)
    materia = relationship("Materia", back_populates="notas")

    def __repr__(self):        
        return f"{self.materia.nombre if self.materia else 'Materia'}: {self.calificacion}"


class Asistencia(Model):
    __tablename__ = "asistencia"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    estado = Column(String(15), nullable=False)       # Presente/Falta/Licencia/Atraso
    
    estudiante_id = Column(Integer, ForeignKey("estudiante.id", ondelete="CASCADE"), nullable=False)
    estudiante = relationship("Estudiante", back_populates="asistencias")
    
    materia_id = Column(Integer, ForeignKey("materia.id", ondelete="CASCADE"), nullable=False)
    materia = relationship("Materia", back_populates="asistencias")

    def __repr__(self):        
        return f"{self.fecha} - {self.estado}"
