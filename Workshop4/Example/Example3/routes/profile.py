import uuid
import magic
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,  send_from_directory 
from werkzeug.utils import secure_filename
from utils.forms import UploadForm
from utils.funcs import login_required, allowed_file,with_db 
from pathlib import Path
from models.user import User


profile_bp = Blueprint('profile', __name__)

UPLOAD_DIR = Path('./uploads/avatars')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed extensions and MIME types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif'}
@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@with_db
def profile(db):
    form = UploadForm()
    username = session['user']
    user = User.find_by_username(db,username)
    avatar_path = user["avatar"]
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files.get('avatar')
        if not file or file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('profile.profile'))
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            flash('Only image files are allowed (.png, .jpg, .jpeg, .gif).', 'danger')
            return redirect(url_for('profile.profile'))
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
        if mime_type not in ALLOWED_MIME_TYPES:
            flash('Invalid file content.', 'danger')
            return redirect(url_for('profile.profile'))
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = UPLOAD_DIR / filename
        file.save(file_path)
        User.update_avatar(db,filename,username)
        flash('Avatar uploaded successfully!', 'success')
        return redirect(url_for('profile.profile'))
    return render_template('profile.html', form=form, user=user, avatar_path=avatar_path)

@profile_bp.route('/avatars/<filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(UPLOAD_DIR, filename)