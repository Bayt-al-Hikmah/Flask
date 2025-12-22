from flask import Blueprint, render_template, request, redirect, url_for, flash, session,  send_from_directory 
from forms.upload import UploadForm
from utils.funcs import login_required, upload_file,with_db 
from pathlib import Path


profile_bp = Blueprint('profile', __name__)
UPLOAD_DIR = Path('./uploads/avatars')

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@with_db
def profile(db):
    form = UploadForm()
    username = session['user']
    cursor = db.cursor()
    cursor.execute("SELECT avatar FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    avatar_path = user["avatar"]
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files.get('avatar')
        if not file or file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('profile.profile'))
        status,filename = upload_file(file)
        if not status:
            flash('Only image files are allowed (.png, .jpg, .jpeg, .gif).', 'danger')
            return redirect(url_for('profile.profile'))
        cursor.execute("UPDATE users SET avatar = ? WHERE username = ?", (filename, username))
        db.commit()
        flash('Avatar uploaded successfully!', 'success')
        return redirect(url_for('profile.profile'))
    return render_template('profile.html', form=form, user=user, avatar_path=avatar_path)

@profile_bp.route('/avatars/<filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(UPLOAD_DIR, filename)