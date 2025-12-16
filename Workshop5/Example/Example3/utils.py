import os
import uuid
from werkzeug.utils import secure_filename

from pathlib import Path

UPLOAD_DIR = Path('./uploads/avatars')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_and_save_avatar(avatar_file):
    if not allowed_file(avatar_file.filename):
        return False,"aa"
    filename = filename = f"{uuid.uuid4().hex}_{secure_filename(avatar_file.filename)}"
    avatar_path = os.path.join(UPLOAD_DIR, filename)
    avatar_file.save(avatar_path)
    return True, avatar_path