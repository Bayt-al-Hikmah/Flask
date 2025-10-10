from flask import Flask, jsonify, request

profiles = {
  "Alice": { "username": "Alice", "email": "alice@example.com", "role": "admin" },
  "Bob": { "username": "Bob", "email": "bob@example.com", "role": "user" },
  "Carol": { "username": "Carol", "email": "carol@example.com", "role": "moderator" },
  "Dave": { "username": "Dave", "email": "dave@example.com", "role": "user" },
}

app = Flask(__name__)

@app.route('/profile/<username>', methods=['GET'])
def get_data(username):
    profile = profiles.get(username)
    details = request.args.get('details', 'false').lower()
    
    if details == 'true' and profile:
        return jsonify(profile)
    elif profile:
        return jsonify({"username": profile["username"]})
    else:
        return jsonify({"error": "Profile not found"}), 404


if __name__ == '__main__':
    app.run(port=3000,debug=True)