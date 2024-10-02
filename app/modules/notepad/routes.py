from app.modules.notepad import notepad_bp
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.modules.notepad.forms import NotepadForm
from app.modules.notepad.services import NotepadService

notepad_service = NotepadService()

''' LIST ALL NOTEPADS '''


@notepad_bp.route('/notepad', methods=['GET'])
@login_required
def index():
    form = NotepadForm()
    notepads = notepad_service.get_all_by_user(current_user.id)
    return render_template('notepad/index.html', notepads=notepads, form=form)


''' CREATE NOTEPAD '''


@notepad_bp.route('/notepad/create', methods=['GET', 'POST'])
@login_required
def create_notepad():
    form = NotepadForm()
    if form.validate_on_submit():
        res = notepad_service.create(title=form.title.data, body=form.body.data, user_id=current_user.id)
        return notepad_service.handle_service_response(
            result=res,
            errors=form.errors,
            success_url_redirect='notepad.index',
            success_msg='Notepad created successfully',
            error_template='notepad/create.html',
            form=form
        )
    return render_template('notepad/create.html', form=form)


''' READ BY ID'''


@notepad_bp.route('/notepad/<int:notepad_id>', methods=['GET'])
@login_required
def get_notepad(notepad_id):
    notepad = notepad_service.get_or_404(notepad_id)
    
    if notepad.user_id != current_user.id:
        flash('You are not authorized to view this notepad', 'error')
        return redirect(url_for('notepad.index'))

    return render_template('notepad/show.html', notepad=notepad)


''' EDIT NOTEPAD '''


@notepad_bp.route('/notepad/edit/<int:notepad_id>', methods=['GET', 'POST'])
@login_required
def edit_notepad(notepad_id):
    notepad = notepad_service.get_or_404(notepad_id)
    
    if notepad.user_id != current_user.id:
        flash('You are not authorized to edit this notepad', 'error')
        return redirect(url_for('notepad.index'))

    form = NotepadForm(obj=notepad)
    if form.validate_on_submit():
        res = notepad_service.update(
            notepad_id, 
            title=form.title.data, 
            body=form.body.data
            )
        return notepad_service.handle_service_response(
            result=res,
            errors=form.errors,
            success_url_redirect='notepad.index',
            success_msg='Notepad updated successfully',
            error_template='notepad/edit.html',
            form=form
        )
    return render_template('notepad/edit.html', form=form, notepad=notepad)


''' DELETE NOTEPAD '''


@notepad_bp.route('/notepad/delete/<int:notepad_id>', methods=['POST'])
@login_required
def delete_notepad(notepad_id):
    notepad = notepad_service.get_or_404(notepad_id)
    if notepad.user_id != current_user.id:
        flash('You are not authorized to delete this notepad', 'error')
        return redirect(url_for('notepad.index'))
    res = notepad_service.delete(notepad)
    if res:
        flash('Notepad successfully deleted', 'success')
    else:
        flash('Notepad deletion failed', 'error')
    return redirect(url_for('notepad.index'))