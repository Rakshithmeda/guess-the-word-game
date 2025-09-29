from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guessword.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    guesses = db.Column(db.Text, nullable=False)  # JSON string of guesses
    is_correct = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='game_sessions')
    word = db.relationship('Word', backref='game_sessions')

# Initialize database and add default words
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('Admin@123'),
                is_admin=True
            )
            db.session.add(admin)
        
        # Add 20 default words if not exists
        default_words = [
            'APPLE', 'BRAIN', 'CRANE', 'DANCE', 'EARTH',
            'FLAME', 'GRACE', 'HEART', 'IMAGE', 'JOKER',
            'KNIFE', 'LEMON', 'MAGIC', 'NOVEL', 'OCEAN',
            'PEACE', 'QUEEN', 'RIVER', 'STONE', 'TIGER'
        ]
        
        for word_text in default_words:
            if not Word.query.filter_by(word=word_text).first():
                word = Word(word=word_text)
                db.session.add(word)
        
        db.session.commit()

# Validation functions
def validate_username(username):
    if len(username) < 5:
        return False, "Username must be at least 5 characters long"
    if not re.search(r'[a-z]', username):
        return False, "Username must contain at least one lowercase letter"
    if not re.search(r'[A-Z]', username):
        return False, "Username must contain at least one uppercase letter"
    return True, ""

def validate_password(password):
    if len(password) < 5:
        return False, "Password must be at least 5 characters long"
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain alphabetic characters"
    if not re.search(r'\d', password):
        return False, "Password must contain numeric characters"
    if not re.search(r'[$%*@]', password):
        return False, "Password must contain one of: $, %, *, @"
    return True, ""

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate username
        valid, msg = validate_username(username)
        if not valid:
            flash(msg, 'danger')
            return render_template('register.html')
        
        # Validate password
        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'danger')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        # Create user
        user = User(
            username=username,
            password=generate_password_hash(password),
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    # Check games played today
    today = datetime.utcnow().date()
    games_today = GameSession.query.filter_by(
        user_id=session['user_id'],
        date=today
    ).count()
    
    can_play = games_today < 3
    
    return render_template('dashboard.html', 
                         games_today=games_today, 
                         can_play=can_play)

@app.route('/play', methods=['GET', 'POST'])
def play():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user can play today
    today = datetime.utcnow().date()
    games_today = GameSession.query.filter_by(
        user_id=session['user_id'],
        date=today
    ).count()
    
    if games_today >= 3:
        flash('You have reached the maximum of 3 games per day', 'warning')
        return redirect(url_for('dashboard'))
    
    # Get or create game session
    if 'current_game_id' not in session:
        # Pick a random word
        words = Word.query.all()
        if not words:
            flash('No words available in database', 'danger')
            return redirect(url_for('dashboard'))
        
        random_word = random.choice(words)
        
        # Create new game session
        game = GameSession(
            user_id=session['user_id'],
            word_id=random_word.id,
            date=today,
            guesses='[]',
            attempts=0
        )
        db.session.add(game)
        db.session.commit()
        
        session['current_game_id'] = game.id
        session['guesses'] = []
    
    game = GameSession.query.get(session['current_game_id'])
    word = Word.query.get(game.word_id)
    
    return render_template('play.html', 
                         guesses=session.get('guesses', []),
                         attempts=len(session.get('guesses', [])))

@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    if 'user_id' not in session or 'current_game_id' not in session:
        return jsonify({'error': 'Invalid session'}), 400
    
    guess = request.json.get('guess', '').upper()
    
    if len(guess) != 5 or not guess.isalpha():
        return jsonify({'error': 'Please enter a valid 5-letter word'}), 400
    
    game = GameSession.query.get(session['current_game_id'])
    word = Word.query.get(game.word_id)
    
    # Process guess
    result = []
    for i, letter in enumerate(guess):
        if letter == word.word[i]:
            result.append({'letter': letter, 'status': 'correct'})
        elif letter in word.word:
            result.append({'letter': letter, 'status': 'present'})
        else:
            result.append({'letter': letter, 'status': 'absent'})
    
    # Update session guesses
    if 'guesses' not in session:
        session['guesses'] = []
    session['guesses'].append(result)
    session.modified = True
    
    # Update database
    game.attempts += 1
    import json
    game.guesses = json.dumps(session['guesses'])
    
    is_correct = guess == word.word
    game_over = is_correct or game.attempts >= 5
    
    if is_correct:
        game.is_correct = True
    
    if game_over:
        db.session.commit()
        session.pop('current_game_id', None)
        session.pop('guesses', None)
    else:
        db.session.commit()
    
    return jsonify({
        'result': result,
        'is_correct': is_correct,
        'game_over': game_over,
        'correct_word': word.word if game_over else None,
        'attempts': game.attempts
    })

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('admin_dashboard.html')

@app.route('/admin/daily_report', methods=['GET', 'POST'])
def daily_report():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        report_date = datetime.utcnow().date()
    
    # Get statistics for the day
    games = GameSession.query.filter_by(date=report_date).all()
    unique_users = len(set(game.user_id for game in games))
    correct_guesses = sum(1 for game in games if game.is_correct)
    
    return render_template('daily_report.html',
                         report_date=report_date,
                         unique_users=unique_users,
                         correct_guesses=correct_guesses,
                         total_games=len(games))

@app.route('/admin/user_report', methods=['GET', 'POST'])
def user_report():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    users = User.query.filter_by(is_admin=False).all()
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        
        # Get user's game sessions grouped by date
        games = GameSession.query.filter_by(user_id=user_id).order_by(GameSession.date.desc()).all()
        
        # Group by date
        from collections import defaultdict
        games_by_date = defaultdict(list)
        for game in games:
            games_by_date[game.date].append(game)
        
        report_data = []
        for date, day_games in games_by_date.items():
            correct = sum(1 for g in day_games if g.is_correct)
            report_data.append({
                'date': date,
                'words_tried': len(day_games),
                'correct_guesses': correct
            })
        
        return render_template('user_report.html',
                             users=users,
                             selected_user=user,
                             report_data=report_data)
    
    return render_template('user_report.html', users=users)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)