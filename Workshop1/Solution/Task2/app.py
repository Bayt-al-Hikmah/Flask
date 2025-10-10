from flask import Flask, jsonify, request

booksDb = {
    '201': { 'id': '201', 'title': 'Clean Code', 'author': 'Robert C. Martin', 'price': 35 },
    '202': { 'id': '202', 'title': 'The Pragmatic Programmer', 'author': 'Andrew Hunt', 'price': 45 },
    '203': { 'id': '203', 'title': 'Design Patterns', 'author': 'Erich Gamma', 'price': 55 }
    }


app = Flask(__name__)

@app.route('/books/<bookID>', methods=['GET'])
def get_data(bookID):
    summary = request.args.get('summary', 'false').lower()
    book = booksDb.get(bookID)

    if summary == 'true' and book:
        return jsonify({"title":book["title"],"author":book["author"]})
    elif book:
        return jsonify(book)
    else:
        return jsonify({"error": "Book not found"}), 404


if __name__ == '__main__':
    app.run(port=3000,debug=True)