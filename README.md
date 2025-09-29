# Guess the Word Game

A web-based word guessing game built with Flask and SQLite.

## Features

- User registration and authentication with validation
- Play up to 3 games per day
- 5 attempts to guess each 5-letter word
- Color-coded feedback (Green: correct position, Orange: wrong position, Grey: not in word)
- Admin dashboard with reports
- Daily reports showing user statistics
- User-specific reports showing game history

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step-by-Step Installation

1. **Extract the project files**
   - Extract the `guessingword.zip` file to a folder on your computer
   - Open Command Prompt or PowerShell in that folder

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your web browser
   - Go to: `http://127.0.0.1:5000`

## Default Admin Credentials

- Username: `admin`
- Password: `Admin@123`

## User Registration Requirements

### Username:
- At least 5 characters
- Must contain both uppercase and lowercase letters
- Example: `JohnDoe`

### Password:
- At least 5 characters
- Must contain alphabetic characters
- Must contain numeric characters
- Must contain one of: $, %, *, @
- Example: `Pass@123`

## How to Play

1. **Register/Login**: Create an account or login with existing credentials
2. **Start Game**: Click "Start New Game" from the dashboard
3. **Make Guesses**: Enter 5-letter words (uppercase only)
4. **Color Feedback**:
   - 🟢 **Green**: Letter is correct and in the right position
   - 🟠 **Orange**: Letter is in the word but wrong position
   - ⚫ **Grey**: Letter is not in the word
5. **Win Condition**: Guess the word correctly within 5 attempts
6. **Daily Limit**: Maximum 3 games per day per user

## Admin Features

1. **Daily Report**:
   - View statistics for any specific date
   - Number of unique users who played
   - Number of correct guesses
   - Total games played

2. **User Report**:
   - Select any user to view their history
   - See date-wise game statistics
   - Track words tried and correct guesses
   - View success rates

## Project Structure

```
guessingword/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── guessword.db          # SQLite database (created automatically)
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── play.html
│   ├── admin_dashboard.html
│   ├── daily_report.html
│   └── user_report.html
└── static/               # Static files
    └── style.css         # CSS styles
```

## Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- password (Hashed)
- is_admin (Boolean)
- created_at (Timestamp)

### Words Table
- id (Primary Key)
- word (5-letter word, uppercase)
- created_at (Timestamp)

### GameSession Table
- id (Primary Key)
- user_id (Foreign Key)
- word_id (Foreign Key)
- date (Date)
- guesses (JSON string)
- is_correct (Boolean)
- attempts (Integer)
- created_at (Timestamp)

## Troubleshooting

### Port Already in Use
If you see an error about port 5000 being in use, you can run on a different port:
```bash
python app.py
```
Then modify the last line in `app.py` to:
```python
app.run(debug=True, port=5001)
```

### Module Not Found Error
Make sure you've activated the virtual environment and installed all requirements:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Database Issues
If you encounter database errors, delete the `guessword.db` file and restart the application. It will create a fresh database.

## Technologies Used

- **Backend**: Python 3, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3
- **JavaScript**: Vanilla JS for dynamic interactions

## Security Features

- Password hashing using Werkzeug security
- Session management
- Input validation
- SQL injection prevention through ORM

## Contact

For issues or questions, please refer to the project documentation.
