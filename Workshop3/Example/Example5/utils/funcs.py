from functools import wraps
from flask import redirect, url_for, session, flash
import magic
from pathlib import Path
from werkzeug.utils import secure_filename
# Allowed extensions and MIME types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif'}

# Upload folder
UPLOAD_DIR = Path('./uploads/avatars')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('You must be logged in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(file):
	if not allowed_file(file.filename):
		return False,''
    mime_type = magic.from_buffer(file.read(1024), mime=True)
	file.seek(0)
	if mime_type not in ALLOWED_MIME_TYPES:
      return False,''
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file_path = UPLOAD_DIR / filename
    file.save(file_path)
    return True,filename
