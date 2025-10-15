class User:
    @staticmethod
    def create(db,username, password):
        cur = db.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password))
        db.commit()

    @staticmethod
    def update_avatar(db,filename,username):
        cur = db.cursor()
        cur.execute("UPDATE users SET avatar = ? WHERE username = ?", (filename, username))
        db.commit()

    @staticmethod
    def find_by_username(db,username):
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        return user