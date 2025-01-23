# Import necessary libraries
from flask import Flask, render_template, request, jsonify, redirect, url_for, session  # Flask components
from chatbot import ask_question  # Import the chatbot function to get responses
import csv  # For reading and writing CSV files
import os  # For file and directory management
import webbrowser  # To open the browser automatically after the server starts
from threading import Timer  # To execute tasks after a delay (open the browser)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Set the upload folder for file storage
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Example dictionary of users (used for login validation)
users = {
    'admin': '1234',  # Default admin user
}

# Function to open the browser automatically when the server starts
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

# Function to check user credentials in a CSV file
def check_user_in_csv(username, password):
    try:
        with open('users.csv', mode='r') as file:
            csv_reader = csv.DictReader(file)
            print("Reading users from CSV...")  # Log for debugging
            for row in csv_reader:
                row = {key.strip(): value.strip() for key, value in row.items()}
                print(f"Checking user: {row['username']}")  # Log for debugging
                if row['username'] == username and row['password'] == password:
                    print("User found in CSV.")  # Log for debugging
                    return True
    except FileNotFoundError:
        print("users.csv file not found.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return False

# Route for login page
@app.route('/')
def login_page():
    if 'username' in session:
        return redirect(url_for('index'))  # Redirect to index if logged in
    return render_template('login.html')

# Route to authenticate the user
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check credentials from users dictionary or CSV file
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('index'))
    elif check_user_in_csv(username, password):
        session['username'] = username
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error="Invalid username or password!")

# Route for logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)  # Remove the username from session
    return render_template('login.html')

# Route for the homepage (index.html)
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login_page'))  # Redirect to login if not logged in
    user_name = session['username']
    is_admin = user_name == 'admin'  # Check if the logged-in user is admin
    return render_template('index.html', user_name=user_name, is_admin=is_admin)

# Route to add a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login_page'))  # Ensure only admin can add users
    
    username = request.form['username']
    password = request.form['password']
    with open('users.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, password])  # Save new user to CSV
    return redirect(url_for('index'))

# Route to delete a user
@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login_page'))  # Ensure only admin can delete users

    username_to_delete = request.form['username']
    if not username_to_delete:
        return render_template('index.html', error="Username is required to delete.")

    users_list = []
    user_found = False
    try:
        with open('users.csv', mode='r') as file:
            csv_reader = csv.reader(file)
            users_list = [row for row in csv_reader if row[0] != username_to_delete]
            user_found = len(users_list) < sum(1 for _ in csv.reader(open('users.csv')))
        
        if user_found:
            with open('users.csv', mode='w', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerows(users_list)  # Rewrite the CSV without the deleted user
            return redirect(url_for('index'))
        else:
            return render_template('index.html', error="User not found.")
    except Exception as e:
        print(f"Error deleting user: {e}")
        return render_template('index.html', error="Error deleting user.")

# Route to update chatbot answers file
@app.route('/update_chatbox', methods=['POST'])
def update_chatbox():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login_page'))  # Ensure only admin can update chatbot answers
    
    if 'chatbot_answers' not in request.files:
        return redirect(url_for('index'))

    chatbot_answers = request.files['chatbot_answers']
    if chatbot_answers.filename == '':
        return redirect(url_for('index'))

    old_file = os.path.join(app.config['UPLOAD_FOLDER'], 'chatbot_answers.txt')
    if os.path.exists(old_file):
        try:
            os.remove(old_file)  # Remove the old chatbot answers file
        except Exception as e:
            print(f"Error removing old file: {e}")
            return redirect(url_for('index'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chatbot_answers.txt')
    try:
        chatbot_answers.save(file_path)  # Save the new file
    except Exception as e:
        print(f"Error saving file: {e}")
        return redirect(url_for('index'))

    return redirect(url_for('index'))

# Route for chatbot page
@app.route('/chatbot')
def chatbot():
    if 'username' not in session:
        return redirect(url_for('login_page'))  # Redirect to login if not logged in
    user_name = session['username']
    return render_template('chatbot.html', user_name=user_name)

# Route to ask the chatbot a question
@app.route('/ask', methods=['POST'])
def ask():
    if 'username' not in session:
        return jsonify({'error': 'You must be logged in to use the chatbot!'}), 403

    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'Invalid question'}), 400
    
    # Get the response from the chatbot model
    response = ask_question(question)
    
    if 'error' in response:
        return jsonify({'error': response['error']}), 500
    
    return jsonify({'answer': response['answer']})

# Start Flask server
if __name__ == '__main__':
    Timer(0, open_browser).start()  # Open browser after 1 second
    print("Starting Flask server...")
    app.run(debug=False)
