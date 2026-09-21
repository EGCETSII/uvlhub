from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from splent_framework.utils.form_helpers import (
    form_error,
    form_success,
)

from app.features.notepad import notepad_bp
from app.features.notepad.forms import NotepadForm
from app.features.notepad.services import NotepadService


notepad_service = NotepadService()

@notepad_bp.route("/notepad", methods=["GET"])
@login_required
def index():
    form = NotepadForm()

    notepads = notepad_service.get_all_by_user(
        current_user.id
    )

    return render_template(
        "notepad/index.html",
        notepads=notepads,
        form=form
    )

'''
CREATE
'''
@notepad_bp.route('/notepad/create', methods=['GET', 'POST'])
@login_required
def create_notepad():
    form = NotepadForm()
    if form.validate_on_submit():
        notepad_service.create(
            title=form.title.data,
            body=form.body.data,
            user_id=current_user.id,
        )
        return form_success('notepad.index', 'Notepad created successfully!')
    if form.errors:
        return form_error('notepad/create.html', form, form.errors)
    return render_template('notepad/create.html', form=form)

'''
READ BY ID
'''
@notepad_bp.route('/notepad/<int:notepad_id>', methods=['GET'])
@login_required
def get_notepad(notepad_id):
    notepad = notepad_service.get_or_404(notepad_id)

    if notepad.user_id != current_user.id:
        flash('You are not authorized to view this notepad', 'error')
        return redirect(url_for('notepad.index'))

    return render_template('notepad/show.html', notepad=notepad)


'''
EDIT
'''
@notepad_bp.route('/notepad/edit/<int:notepad_id>', methods=['GET', 'POST'])
@login_required
def edit_notepad(notepad_id):
    notepad = notepad_service.get_or_404(notepad_id)
    if notepad.user_id != current_user.id:
        flash('You are not authorized to edit this notepad', 'error')
        return redirect(url_for('notepad.index'))

    form = NotepadForm(obj=notepad)
    if form.validate_on_submit():
        notepad_service.update(
            notepad_id,
            title=form.title.data,
            body=form.body.data,
        )
        return form_success('notepad.index', 'Notepad updated successfully!')
    if form.errors:
        return form_error('notepad/edit.html', form, form.errors, notepad=notepad)
    return render_template('notepad/edit.html', form=form, notepad=notepad)

'''
DELETE
'''
@notepad_bp.route('/notepad/delete/<int:notepad_id>', methods=['POST'])
@login_required
def delete_notepad(notepad_id):
    notepad = notepad_service.get_or_404(notepad_id)
    if notepad.user_id != current_user.id:
        flash('You are not authorized to delete this notepad', 'error')
        return redirect(url_for('notepad.index'))

    if notepad_service.delete(notepad_id):
        return form_success('notepad.index', 'Notepad deleted successfully!')

    return form_success('notepad.index', 'Error deleting notepad', category='error')
