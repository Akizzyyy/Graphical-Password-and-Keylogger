How to Run the Project
This project includes:

Graphical Password Backend (Node.js + MongoDB)

Shoulder Surfer AI (Python script for monitoring and training)

Steps to Run

1. Start the Frontend
Open a terminal and navigate to the graphical-passwords directory:
cd graphical-passwords
npm install
npm run dev
This starts the React app (usually at http://localhost:5173).


2. Start the Backend
Open a terminal and navigate to the graphical-password-backend directory:
cd graphical-password-backend
nodemon server.js
This starts the Express server that handles registration and authentication.

3. Run the Shoulder Surfer AI
Open another terminal and run the Python script:
python shoulder_surfer.py