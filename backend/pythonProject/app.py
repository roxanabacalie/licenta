import json

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, 'templates')
app.template_folder = template_folder

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/directions', methods=['POST'])
def save_directions():
    data = request.get_json()
    try:
        with open('directions.json', 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify({"message": "Data saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
