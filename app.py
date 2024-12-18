from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
from collections import Counter
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from email_service import send_daily_report
import pytz
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smoking_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.relationship('Progress', backref='user', lazy=True)
    daily_logs = db.relationship('DailyLog', backref='user', lazy=True)
    email_notifications = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='Asia/Kolkata')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    daily_cigarettes = db.Column(db.Integer, default=0)
    target_cigarettes = db.Column(db.Integer, default=0)
    daily_reflection = db.Column(db.Text, default='')
    date = db.Column(db.Date, default=datetime.utcnow().date)
    cost_per_cigarette = db.Column(db.Float, default=18.0)  # Default 18 INR
    currency = db.Column(db.String(10), default='INR')
    start_date = db.Column(db.Date, default=datetime.utcnow().date)

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    cigarettes_smoked = db.Column(db.Integer, default=0)
    cravings_logged = db.Column(db.Integer, default=0)
    cravings_resisted = db.Column(db.Integer, default=0)
    locations = db.Column(db.Text, default='')
    emotions = db.Column(db.Text, default='')

with app.app_context():
    db.create_all()

def get_or_create_progress():
    if not current_user.is_authenticated:
        return None
        
    today = datetime.now().date()
    progress = Progress.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if not progress:
        progress = Progress(
            user_id=current_user.id,
            daily_cigarettes=0,
            target_cigarettes=0,
            daily_reflection='',
            date=today,
            cost_per_cigarette=18.0,
            currency='INR',
            start_date=today
        )
        db.session.add(progress)
        db.session.commit()
    
    return progress

def get_or_create_daily_log():
    if not current_user.is_authenticated:
        return None
        
    today = datetime.now().date()
    daily_log = DailyLog.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if not daily_log:
        daily_log = DailyLog(
            user_id=current_user.id,
            date=today
        )
        db.session.add(daily_log)
        db.session.commit()
    
    return daily_log

def calculate_money_saved(progress, daily_log):
    if not progress or not daily_log:
        return 0
    
    # Simple calculation: (target - actual) * cost per cigarette
    cigarettes_saved = progress.target_cigarettes - daily_log.cigarettes_smoked
    # Only return positive values, if smoked more than target, return 0
    return max(0, cigarettes_saved * progress.cost_per_cigarette)

def calculate_stats():
    if not current_user.is_authenticated:
        return {
            'dates': [],
            'cigarettes_data': [],
            'targets_data': [],
            'cravings_data': [],
            'total_reduction': 0,
            'total_saved': 0,
            'top_locations': [],
            'top_emotions': [],
            'best_days': [],
            'daily_logs': [],
            'days_count': 0,
            'currency_symbol': '$',
            'total_cravings_resisted': 0,
            'target_cigarettes': 0,
            'start_date': None,
            'end_date': None,
            'total_cigarettes': 0,
            'avg_cigarettes': 0,
            'money_saved': 0
        }
    
    progress = Progress.query.filter_by(user_id=current_user.id).order_by(Progress.date).all()
    if not progress:
        return {
            'dates': [],
            'cigarettes_data': [],
            'targets_data': [],
            'cravings_data': [],
            'total_reduction': 0,
            'total_saved': 0,
            'top_locations': [],
            'top_emotions': [],
            'best_days': [],
            'daily_logs': [],
            'days_count': 0,
            'currency_symbol': '$',
            'total_cravings_resisted': 0,
            'target_cigarettes': 0,
            'start_date': None,
            'end_date': None,
            'total_cigarettes': 0,
            'avg_cigarettes': 0,
            'money_saved': 0
        }

    # Get all daily logs
    daily_logs = DailyLog.query.filter_by(user_id=current_user.id).order_by(DailyLog.date).all()
    
    # Calculate basic stats
    start_date = progress[0].date if progress else None
    end_date = progress[-1].date if progress else None
    total_cigarettes = sum(log.cigarettes_smoked for log in daily_logs) if daily_logs else 0
    avg_cigarettes = round(total_cigarettes / len(daily_logs), 1) if daily_logs else 0
    
    # Prepare data for charts
    dates = [log.date.strftime('%Y-%m-%d') for log in daily_logs]
    cigarettes_data = [log.cigarettes_smoked for log in daily_logs]
    targets_data = [p.target_cigarettes for p in progress[:len(daily_logs)]]
    cravings_data = [log.cravings_resisted for log in daily_logs]
    
    # Calculate total reduction
    total_reduction = 0
    if len(cigarettes_data) >= 2:
        initial = cigarettes_data[0]
        current = cigarettes_data[-1]
        total_reduction = ((initial - current) / initial * 100) if initial > 0 else 0
    
    # Calculate money saved (cumulative)
    total_money_saved = 0
    for log, prog in zip(daily_logs, progress):
        cigarettes_saved = prog.target_cigarettes - log.cigarettes_smoked
        # Allow negative values when exceeded target
        daily_saved = cigarettes_saved * prog.cost_per_cigarette
        total_money_saved += daily_saved

    # Calculate today's money saved
    today_progress = get_or_create_progress()
    today_log = get_or_create_daily_log()
    today_cigarettes_saved = today_progress.target_cigarettes - today_log.cigarettes_smoked
    today_money_saved = today_cigarettes_saved * today_progress.cost_per_cigarette

    # Analyze locations and emotions
    all_locations = []
    all_emotions = []
    for log in daily_logs:
        if log.locations:
            all_locations.extend([loc.strip() for loc in log.locations.split(',')])
        if log.emotions:
            all_emotions.extend([emotion.strip() for emotion in log.emotions.split(',')])
    
    # Get top locations and emotions
    location_counts = Counter(all_locations)
    emotion_counts = Counter(all_emotions)
    top_locations = location_counts.most_common(5)
    top_emotions = emotion_counts.most_common(5)
    
    # Find best days
    best_days = sorted([(log.date, log.cigarettes_smoked) 
                       for log in daily_logs], 
                      key=lambda x: (x[1], datetime.combine(x[0], datetime.min.time()).timestamp()))[:5]
    
    total_cravings_resisted = sum(log.cravings_resisted for log in daily_logs)
    
    return {
        'dates': dates,
        'cigarettes_data': cigarettes_data,
        'targets_data': targets_data,
        'cravings_data': cravings_data,
        'total_reduction': round(total_reduction, 1),
        'total_saved': round(total_money_saved, 2),
        'top_locations': top_locations,
        'top_emotions': top_emotions,
        'best_days': best_days,
        'daily_logs': daily_logs,
        'days_count': len(daily_logs),
        'currency_symbol': progress[0].currency if progress else '$',
        'total_cravings_resisted': total_cravings_resisted,
        'target_cigarettes': progress[-1].target_cigarettes if progress else 0,
        'start_date': start_date,
        'end_date': end_date,
        'total_cigarettes': total_cigarettes,
        'avg_cigarettes': avg_cigarettes,
        'money_saved': round(today_money_saved, 2)
    }

def get_user_stats(user):
    today = datetime.now().date()
    today_log = DailyLog.query.filter_by(user_id=user.id, date=today).first()
    progress = Progress.query.filter_by(user_id=user.id, date=today).first()
    
    if not today_log or not progress:
        return None
        
    # Calculate streak
    streak = 0
    current_date = today
    while True:
        log = DailyLog.query.filter_by(user_id=user.id, date=current_date).first()
        if not log or log.cigarettes_smoked > 0:
            break
        streak += 1
        current_date -= timedelta(days=1)
    
    # Get common trigger
    logs = DailyLog.query.filter_by(user_id=user.id).all()
    all_locations = []
    for log in logs:
        if log.locations:
            all_locations.extend(json.loads(log.locations))
    common_trigger = Counter(all_locations).most_common(1)[0][0] if all_locations else "No data"
    
    # Calculate success rate
    if today_log.cravings_logged > 0:
        success_rate = (today_log.cravings_resisted / today_log.cravings_logged) * 100
    else:
        success_rate = 0
    
    return {
        'cigarettes_smoked': today_log.cigarettes_smoked,
        'target_cigarettes': progress.target_cigarettes,
        'cravings_resisted': today_log.cravings_resisted,
        'currency': progress.currency,
        'money_saved': calculate_money_saved(progress, today_log),
        'streak': streak,
        'common_trigger': common_trigger,
        'success_rate': round(success_rate, 1)
    }

@scheduler.task('cron', id='send_daily_emails', hour=18, minute=0, timezone='Asia/Kolkata')
def send_daily_emails():
    with app.app_context():
        users = User.query.filter_by(email_notifications=True).all()
        for user in users:
            stats = get_user_stats(user)
            if stats:
                send_daily_report(user, stats)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Successfully logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('signup.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Account created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    progress = get_or_create_progress()
    if not progress:
        flash('Please log in to track your progress', 'error')
        return redirect(url_for('login'))
        
    daily_log = get_or_create_daily_log()
    stats = calculate_stats()  # Get stats for money saved
    
    return render_template('index.html', 
                         progress=progress, 
                         today_log=daily_log,
                         stats=stats)

@app.route('/set_target', methods=['POST'])
@login_required
def set_target():
    progress = get_or_create_progress()
    progress.daily_cigarettes = int(request.form.get('current_cigarettes', 0))
    progress.target_cigarettes = int(request.form.get('target_cigarettes', 0))
    progress.cost_per_cigarette = float(request.form.get('cost_per_cigarette', 18.0))
    progress.currency = request.form.get('currency', 'INR')
    
    # Update start date only if it's not set
    if not progress.start_date:
        progress.start_date = datetime.utcnow().date()
    
    db.session.commit()
    flash('Target and cost settings updated successfully!')
    return redirect(url_for('index'))

@app.route('/log_smoke', methods=['POST'])
@login_required
def log_smoke():
    daily_log = get_or_create_daily_log()
    daily_log.cigarettes_smoked += 1
    db.session.commit()
    
    # Return JSON if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        progress = get_or_create_progress()
        cigarettes_saved = progress.target_cigarettes - daily_log.cigarettes_smoked
        money_saved = max(0, cigarettes_saved * progress.cost_per_cigarette)
        return jsonify({
            'cigarettes_smoked': daily_log.cigarettes_smoked,
            'money_saved': round(money_saved, 2)
        })
    
    return redirect(url_for('index'))

@app.route('/log_craving', methods=['POST'])
@login_required
def log_craving():
    daily_log = get_or_create_daily_log()
    daily_log.cravings_logged += 1
    daily_log.cravings_resisted += 1  # Increment resisted count when logging a craving
    
    location = request.form.get('location', '')
    emotion = request.form.get('emotion', '')
    
    if location:
        locations = daily_log.locations.split(',') if daily_log.locations else []
        locations.append(location)
        daily_log.locations = ','.join(locations)
    
    if emotion:
        emotions = daily_log.emotions.split(',') if daily_log.emotions else []
        emotions.append(emotion)
        daily_log.emotions = ','.join(emotions)
    
    db.session.commit()
    flash('Great job resisting a craving! Stay strong!')
    return redirect(url_for('index'))

@app.route('/reflect', methods=['POST'])
@login_required
def reflect():
    progress = get_or_create_progress()
    progress.daily_reflection = request.form.get('reflection', '')
    db.session.commit()
    flash('Reflection saved. Keep going!')
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
@login_required
def reset():
    try:
        # Delete all records from both tables
        DailyLog.query.filter_by(user_id=current_user.id).delete()
        Progress.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        # Create fresh records for today
        get_or_create_progress()
        get_or_create_daily_log()
        
        flash('Journey reset successfully. Every moment is a new beginning.')
    except Exception as e:
        flash('Error resetting journey. Please try again.')
        db.session.rollback()
    
    return redirect(url_for('index'))

@app.route('/stats')
@login_required
def view_stats():
    stats = calculate_stats()
    if not stats:
        flash('No data available yet', 'info')
        return redirect(url_for('index'))
    return render_template('stats.html', stats=stats)

@app.route('/guide')
@login_required
def guide():
    return render_template('guide.html')

@app.route('/test_email')
@login_required
def test_email():
    stats = get_user_stats(current_user)
    if stats:
        success = send_daily_report(current_user, stats)
        if success:
            flash('Test email sent successfully!', 'success')
        else:
            flash('Failed to send test email. Please check the logs.', 'error')
    else:
        flash('No stats available to send.', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
