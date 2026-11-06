from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from wtforms import SelectField
from wtforms.validators import DataRequired, NumberRange

# Importación correcta desde el archivo de extensiones
from .extensions import appbuilder, db
from .models import Curso, Docente, Estudiante, Materia, Nota, Asistencia

ESTADOS = [("Presente", "Presente"), ("Falta", "Falta"), ("Licencia", "Licencia"), ("Atraso", "Atraso")]
# Claves numéricas para que coincidan con coerce=int
TRIMESTRES = [(1, "Primer trimestre"), (2, "Segundo trimestre"), (3, "Tercer trimestre")]


class EstudianteView(ModelView):
    datamodel = SQLAInterface(Estudiante)
    list_columns = ["nombre", "ci", "curso", "tutor"]
    search_columns = ["nombre", "ci", "curso"]
    label_columns = {"ci": "C.I.", "fecha_nacimiento": "Fecha de nacimiento", "telefono_tutor": "Teléfono del tutor"}


class MateriaView(ModelView):
    datamodel = SQLAInterface(Materia)
    list_columns = ["nombre", "curso", "docente", "horas_semanales"]
    label_columns = {"horas_semanales": "Horas semanales"}


class CursoView(ModelView):
    datamodel = SQLAInterface(Curso)
    list_columns = ["nombre", "paralelo", "gestion"]
    related_views = [EstudianteView, MateriaView]
    label_columns = {"gestion": "Gestión"}


class DocenteView(ModelView):
    datamodel = SQLAInterface(Docente)
    list_columns = ["nombre", "especialidad", "telefono", "email"]
    related_views = [MateriaView]
    label_columns = {"telefono": "Teléfono"}


_trim = {"trimestre": SelectField("Trimestre", choices=TRIMESTRES, coerce=int, validators=[DataRequired()])}
_est = {"estado": SelectField("Estado", choices=ESTADOS, validators=[DataRequired()])}


class NotaView(ModelView):
    datamodel = SQLAInterface(Nota)
    list_columns = ["estudiante", "materia", "trimestre", "calificacion"]
    search_columns = ["estudiante", "materia", "trimestre", "calificacion"]
    add_form_extra_fields = _trim
    edit_form_extra_fields = _trim
    validators_columns = {"calificacion": [NumberRange(min=0, max=100, message="Debe estar entre 0 y 100")]}
    label_columns = {"calificacion": "Calificación"}


class AsistenciaView(ModelView):
    datamodel = SQLAInterface(Asistencia)
    list_columns = ["fecha", "estudiante", "materia", "estado"]
    search_columns = ["fecha", "estudiante", "materia", "estado"]
    add_form_extra_fields = _est
    edit_form_extra_fields = _est
    base_order = ("fecha", "desc")


# Registro de vistas en el menú
appbuilder.add_view(CursoView, "Cursos", icon="fa-university", category="Académico")
appbuilder.add_view(EstudianteView, "Estudiantes", icon="fa-graduation-cap", category="Académico")
appbuilder.add_view(DocenteView, "Docentes", icon="fa-user", category="Académico")
appbuilder.add_view(MateriaView, "Materias", icon="fa-book", category="Académico")
appbuilder.add_view(NotaView, "Notas", icon="fa-pencil", category="Evaluación")
appbuilder.add_view(AsistenciaView, "Asistencia", icon="fa-check-square-o", category="Evaluación")

# Comenta estas líneas si aún no has creado los archivos reports.py ni ai.py
from .reports import ReporteNotasView, ReporteAsistenciaView, ReporteRendimientoView
# from .ai import AsistenteIAView

appbuilder.add_view(ReporteNotasView, "Notas por curso y materia", category="Reportes", icon="fa-table")
appbuilder.add_view(ReporteAsistenciaView, "Asistencia por estudiante", category="Reportes", icon="fa-calendar")
appbuilder.add_view(ReporteRendimientoView, "Rendimiento académico", category="Reportes", icon="fa-bar-chart")
appbuilder.add_view(AsistenteIAView, "Asistente IA", category="Evaluación", icon="fa-magic")
