from datetime import date, timedelta

from flask import request
from flask_appbuilder import BaseView, expose, has_access
from sqlalchemy import func, case

from . import db
from .models import Curso, Estudiante, Materia, Nota, Asistencia

NOTA_MINIMA = 51  # aprobación (escala 0-100)


def _fecha(valor, por_defecto):
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        return por_defecto


def _cursos():
    return db.session.query(Curso).order_by(Curso.nombre, Curso.paralelo).all()


class ReporteNotasView(BaseView):
    """Reporte 1: notas filtradas por curso, materia y trimestre, con promedio."""
    route_base = "/reporte/notas"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        curso_id = request.args.get("curso", type=int)
        materia_id = request.args.get("materia", type=int)
        trimestre = request.args.get("trimestre", type=int)

        q = (
            db.session.query(Estudiante.nombre, Curso, Materia.nombre, Nota.trimestre, Nota.calificacion)
            .join(Nota, Nota.estudiante_id == Estudiante.id)
            .join(Materia, Nota.materia_id == Materia.id)
            .join(Curso, Estudiante.curso_id == Curso.id)
        )
        if curso_id:
            q = q.filter(Estudiante.curso_id == curso_id)
        if materia_id:
            q = q.filter(Materia.id == materia_id)
        if trimestre:
            q = q.filter(Nota.trimestre == trimestre)
        filas = q.order_by(Curso.nombre, Estudiante.nombre, Materia.nombre, Nota.trimestre).all()
        promedio = sum(f[4] for f in filas) / len(filas) if filas else 0

        return self.render_template(
            "reporte_notas.html", filas=filas, promedio=promedio, cursos=_cursos(),
            materias=db.session.query(Materia).order_by(Materia.nombre).all(),
            curso_id=curso_id, materia_id=materia_id, trimestre=trimestre,
        )


class ReporteAsistenciaView(BaseView):
    """Reporte 2: conteo de presentes, faltas, licencias y atrasos por estudiante en un rango de fechas."""
    route_base = "/reporte/asistencia"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        hoy = date.today()
        desde = _fecha(request.args.get("desde"), hoy - timedelta(days=60))
        hasta = _fecha(request.args.get("hasta"), hoy)
        curso_id = request.args.get("curso", type=int)

        def cuenta(estado):
            return func.coalesce(func.sum(case((Asistencia.estado == estado, 1), else_=0)), 0)

        q = (
            db.session.query(
                Estudiante.nombre, Curso, cuenta("Presente"), cuenta("Falta"),
                cuenta("Licencia"), cuenta("Atraso"), func.count(Asistencia.id),
            )
            .join(Asistencia, Asistencia.estudiante_id == Estudiante.id)
            .join(Curso, Estudiante.curso_id == Curso.id)
            .filter(Asistencia.fecha >= desde, Asistencia.fecha <= hasta)
        )
        if curso_id:
            q = q.filter(Estudiante.curso_id == curso_id)
        filas = q.group_by(Estudiante.id, Estudiante.nombre, Curso.id).order_by(cuenta("Falta").desc()).all()

        return self.render_template(
            "reporte_asistencia.html", filas=filas, cursos=_cursos(), curso_id=curso_id,
            desde=desde.isoformat(), hasta=hasta.isoformat(),
        )


class ReporteRendimientoView(BaseView):
    """Reporte 3: promedio general por estudiante y condición (aprobado/reprobado)."""
    route_base = "/reporte/rendimiento"
    default_view = "index"

    @expose("/")
    @has_access
    def index(self):
        curso_id = request.args.get("curso", type=int)
        condicion = request.args.get("condicion", "")

        prom = func.avg(Nota.calificacion)
        q = (
            db.session.query(Estudiante.nombre, Curso, prom, func.count(Nota.id))
            .join(Nota, Nota.estudiante_id == Estudiante.id)
            .join(Curso, Estudiante.curso_id == Curso.id)
            .group_by(Estudiante.id, Estudiante.nombre, Curso.id)
        )
        if curso_id:
            q = q.filter(Estudiante.curso_id == curso_id)
        if condicion == "Aprobado":
            q = q.having(prom >= NOTA_MINIMA)
        elif condicion == "Reprobado":
            q = q.having(prom < NOTA_MINIMA)
        filas = q.order_by(prom.desc()).all()

        return self.render_template(
            "reporte_rendimiento.html", filas=filas, cursos=_cursos(), curso_id=curso_id,
            condicion=condicion, minima=NOTA_MINIMA,
        )
