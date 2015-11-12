from flask import jsonify, request, current_app, url_for
from . import api
from ..models import Teachers


@api.route('teachers/<int:id>')
def get_teacher_id():
    teacher = Teacher.query.get_or_404(id)
    return jsonify(teacher.to_json())
