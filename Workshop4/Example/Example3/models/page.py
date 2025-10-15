class Page:
    @staticmethod
    def create(db,title, content):
        cur = db.cursor()
        cur.execute("INSERT INTO pages (title, content) VALUES (?, ?)", (title, content))
        db.commit()

    @staticmethod
    def find_by_title(db,page_name):
        cur = db.cursor()
        cur.execute("SELECT content FROM pages WHERE title = ?", (page_name,))
        page = cur.fetchone()
        return page