<<<<<<< HEAD
# Student Test & Quiz App

A simple web application built with Flask that allows students to take quizzes in physics, chemistry, and maths. Users can select a subject, answer multiple-choice questions, and view their scores.

## Features

- Choose between physics, chemistry, and maths quizzes.
- Submit answers and see results immediately.
- Questions can be updated or extended by editing the Python data structure.

## Setup

1. Ensure you have Python 3 installed.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Navigate to `http://127.0.0.1:5000` in your browser.

## Customization

- Add or modify questions in `app.py` inside the `QUESTIONS` dictionary.
- Students are asked for their name at the start of a quiz; results (answers, score, timestamp) are saved to `results.json` automatically.
- View all submitted results by visiting the **"View all submitted results"** link on the home page or going to `/grades`.
- Styling is located in `static/css/style.css`.

## Future Improvements

- Load questions from a database or external file.
- Add user authentication and progress tracking.
- Enhance UI/UX with JavaScript interactivity.

---

Made for GET 103 student test and quiz purposes.
=======
My project zip file
>>>>>>> 842aa6be0ff0fea6185ce5348255992092dda77e
