import requests
from flask import request, current_app
from flask_appbuilder import BaseView, expose, has_access
from sqlalchemy import func

from . import db
from .models import Estudiante, Materia, Nota, Asistencia
from .reports import NOTA_MINIMA


def _datos(est):
    notas = (
        db.session.query(Materia.nombre, func.avg(Nota.calificacion))
        .join(Nota, Nota.materia_id == Materia.id)
        .filter(Nota.estudiante_id == est.id).group_by(Materia.nombre).all()
    )
    asist = dict(
        db.session.query(Asistencia.estado, func.count(Asistencia.id))
        .filter(Asistencia.estudiante_id == est.id).group_by(Asistencia.estado).all()
    )
    return [(m, float(p)) for m, p in notas], asist


def _local(est, notas, asist):
    if not notas:
        return "El estudiante aún no tiene notas registradas."
    out = []
    bajas = [f"{m} ({p:.0f})" for m, p in notas if p < NOTA_MINIMA]
    if bajas:
        out.append("Refuerzo recomendado en: " + ", ".join(bajas) + ".")
    else:
        out.append("Rendimiento satisfactorio en todas las materias; motivar a mantener el nivel.")
    faltas = asist.get("Falta", 0)
    if faltas >= 3:
        out.append(f"Registra {faltas} faltas: conversar con el tutor sobre la asistencia.")
    if asist.get("Atraso", 0) >= 3:
        out.append("Se repiten los atrasos: acordar un plan de puntualidad.")
    return " ".join(out)


def _gemini(prompt):
    key = current_app.config.get("GEMINI_API_KEY")
    if not key:
        return None
    model = current_app.config.get("GEMINI_MODEL", "gemini-2.0-flash")
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


class AsistenteIAView(BaseView):
    route_base = "/asistente"
    default_view = "index"

    @expose("/", methods=["GET", "POST"])
    @has_access
    def index(self):
        estudiantes = db.session.query(Estudiante).order_by(Estudiante.nombre).all()
        est_id = request.form.get("estudiante", type=int)
        respuesta = fuente = error = resumen = None

        if request.method == "POST" and est_id:
            est = db.session.get(Estudiante, est_id)
            notas, asist = _datos(est)
            resumen = {"notas": notas, "asistencia": asist}
            texto_notas = "; ".join(f"{m}: {p:.0f}/100" for m, p in notas) or "sin notas"
            texto_asist = ", ".join(f"{k}: {v}" for k, v in asist.items()) or "sin registros"
            prompt = (
                "Eres un orientador pedagógico. En español y máximo 150 palabras, da: 1) diagnóstico breve, "
                "2) tres recomendaciones concretas para docente y tutor, 3) una frase de motivación para el estudiante. "
                f"Aprobación mínima: {NOTA_MINIMA}/100.\n"
                f"Estudiante de {est.curso}. Promedios por materia: {texto_notas}. Asistencia: {texto_asist}."
            )
            try:
                respuesta = _gemini(prompt)
                fuente = "Google Gemini (API gratuita)"
            except Exception as e:
                error = f"No se pudo usar la IA en línea ({e.__class__.__name__}). Se muestra el motor local."
            if not respuesta:
                respuesta, fuente = _local(est, notas, asist), "Motor local de reglas (respaldo)"

        return self.render_template(
            "asistente.html", estudiantes=estudiantes, est_id=est_id, respuesta=respuesta,
            fuente=fuente, error=error, resumen=resumen, minima=NOTA_MINIMA,
        )
