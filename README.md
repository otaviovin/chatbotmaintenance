# Flask Web Application with User Management and Chatbot

This Flask-based web application provides functionality for user authentication, management (add/delete users), and interaction with a chatbot. It includes an admin panel for managing users and updating chatbot answers.

## Features
- **User Authentication**: Users can log in with credentials stored in a CSV file. Admin users can add and delete other users.
- **Role-based Access Control**: Only admin users can manage other users and update chatbot answers.
- **Chatbot**: Users can interact with a chatbot and get responses to their questions.
- **File Upload**: Admin users can upload a file containing updated answers for the chatbot.
- **Automatic Browser Opening**: The application automatically opens in the browser once the server is started.

## Requirements
- Python 3.x
- Flask
- Web browser for accessing the app

## How to Run
1. Install the required dependencies by running:
   ```bash
   pip install flask

## Run the Dockerfile

    ```bash
   docker build -t chatbotmaintenance-app .

    ```bash
   docker run -d -p 5000:5000 --name container-chatbotmaintenance chatbotmaintenance-app
