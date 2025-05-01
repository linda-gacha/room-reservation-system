import os
import secrets
from flask import Flask, jsonify, url_for, session
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(_name_)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'postgresql://meeting_user:password@localhost:5432/user_db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
app.config['DEBUG'] = True

db = SQLAlchemy(app)
oauth = OAuth(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    role = db.Column(db.String(50), nullable=False, default='visitor')
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role
        }

# Corrected OAuth Setup
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    api_base_url='https://www.googleapis.com/oauth2/v3/',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',
        'access_type': 'offline'
    }
)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/auth/google')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    session['oauth_state'] = secrets.token_urlsafe(16)
    return google.authorize_redirect(redirect_uri, state=session['oauth_state'])

@app.route('/auth/google/callback')
def google_authorize():
    try:
        token = google.authorize_access_token()
        if not token:
            return jsonify({'error': 'Access denied'}), 403
        
        # Verify state parameter
        if session.get('oauth_state') != request.args.get('state'):
            return jsonify({'error': 'Invalid state parameter'}), 400
            
        user_info = google.parse_id_token(token)
        user = User.query.filter_by(email=user_info['email']).first()
        
        if not user:
            user = User(
                email=user_info['email'],
                name=user_info.get('name'),
                role='visitor'
            )
            db.session.add(user)
            db.session.commit()
        
        session['user_id'] = user.id
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if _name_ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
