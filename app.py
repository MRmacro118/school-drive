from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import os
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a more secure secret key for production

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

USERS_FILE = 'users.json'  # Path to the users JSON file

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_users():
    """Load users from the JSON file."""
    with open(USERS_FILE, 'r') as file:
        users_data = json.load(file)
    return users_data["users"]

def validate_user(username, password):
    """Validate the username and password against the JSON data."""
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return True
    return False

@app.route('/')
def home():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('home.html', files=files)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if validate_user(username, password):
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            flash('File uploaded successfully', 'success')
            return redirect(url_for('home'))
    
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete', methods=['POST'])
def delete_file():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    filename = request.form['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'File "{filename}" deleted successfully', 'success')
    else:
        flash(f'File "{filename}" not found', 'error')
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
