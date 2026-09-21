from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.features.notepad import notepad_bp
from app.features.notepad.forms import NotepadForm
from app.features.notepad.services import NotepadService

notepad_service = NotepadService()


@notepad_bp.route("/notepad", methods=["GET"])
def index():
    form = NotepadForm()
    if current_user.is_authenticated:
        notepads = notepad_service.get_all_by_user(current_user.id)
    else:
        notepads = []
    return render_template("notepad/index.html", form=form, notepads=notepads)


@notepad_bp.route("/notepad/create", methods=["POST"])
@login_required
def create():
    form = NotepadForm()
    if form.validate_on_submit():
        notepad_service.create(form.title.data, form.body.data, current_user.id)
        flash("Note created successfully!", "success")
        return redirect(url_for("notepad.index"))
    return render_template("notepad/index.html", form=form)


@notepad_bp.route("/notepad/delete/<int:notepad_id>", methods=["POST"])
@login_required
def delete(notepad_id):
    if notepad_service.delete(notepad_id, current_user.id):
        flash("Nota eliminada correctamente", "success")
    else:
        flash("No se pudo eliminar la nota", "danger")
    return redirect(url_for("notepad.index"))
