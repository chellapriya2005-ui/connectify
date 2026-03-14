# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///connectify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Create upload folders
os.makedirs('static/uploads/videos', exist_ok=True)
os.makedirs('static/uploads/reels', exist_ok=True)
os.makedirs('static/uploads/stories', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(500), default='https://randomuser.me/api/portraits/lego/1.jpg')
    bio = db.Column(db.Text, default='Hello! I am new to Connectify')
    followers = db.Column(db.Integer, default=0)
    following = db.Column(db.Integer, default=0)
    online = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200))
    filename = db.Column(db.String(500))
    file_path = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    video_type = db.Column(db.String(20))
    music = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        user = User.query.get(self.user_id)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': user.username if user else 'unknown',
            'full_name': user.full_name if user else 'Unknown',
            'profile_pic': user.profile_pic if user else '',
            'title': self.title,
            'file_path': self.file_path,
            'views': self.views,
            'likes': self.likes,
            'video_type': self.video_type,
            'music': self.music,
            'created_at': self.created_at.isoformat()
        }

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(500))
    file_path = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    
    def to_dict(self):
        user = User.query.get(self.user_id)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': user.username if user else 'unknown',
            'profile_pic': user.profile_pic if user else '',
            'file_path': self.file_path,
            'views': self.views,
            'created_at': self.created_at.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database created!")

# ==================== AUTH ROUTES ====================
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'error': 'Username taken'}), 400
    
    user = User(
        username=data['username'],
        password=generate_password_hash(data['password']),
        full_name=data.get('full_name', data['username']),
        bio=data.get('bio', 'New to Connectify'),
        profile_pic=f'https://randomuser.me/api/portraits/{"men" if random.choice([True, False]) else "women"}/{random.randint(1,99)}.jpg'
    )
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return jsonify({'success': True, 'user': {'id': user.id, 'name': user.full_name, 'pic': user.profile_pic, 'username': user.username}})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        user.online = True
        db.session.commit()
        socketio.emit('user_status', {'user_id': user.id, 'online': True})
        return jsonify({'success': True, 'user': {'id': user.id, 'name': user.full_name, 'pic': user.profile_pic, 'username': user.username}})
    return jsonify({'success': False})

@app.route('/logout')
def logout():
    if session.get('user_id'):
        user = User.query.get(session['user_id'])
        if user:
            user.online = False
            db.session.commit()
            socketio.emit('user_status', {'user_id': user.id, 'online': False})
    session.clear()
    return jsonify({'success': True})

# ==================== DELETE ACCOUNT ROUTE ====================
@app.route('/delete-account', methods=['POST'])
def delete_account():
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Delete user's videos from filesystem
        videos = Video.query.filter_by(user_id=user_id).all()
        for video in videos:
            file_path = os.path.join('static/uploads', video.video_type + 's', video.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete stories
        stories = Story.query.filter_by(user_id=user_id).all()
        for story in stories:
            file_path = os.path.join('static/uploads/stories', story.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete all user data from database
        Video.query.filter_by(user_id=user_id).delete()
        Story.query.filter_by(user_id=user_id).delete()
        Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).delete()
        Follow.query.filter((Follow.follower_id == user_id) | (Follow.followed_id == user_id)).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        # Clear session
        session.clear()
        
        # Broadcast offline status
        socketio.emit('user_status', {'user_id': user_id, 'online': False})
        
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== FOLLOW ROUTES ====================
@app.route('/api/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    if session['user_id'] == user_id:
        return jsonify({'error': 'Cannot follow yourself'}), 400
    
    existing = Follow.query.filter_by(follower_id=session['user_id'], followed_id=user_id).first()
    if existing:
        db.session.delete(existing)
        User.query.get(session['user_id']).following -= 1
        User.query.get(user_id).followers -= 1
        db.session.commit()
        return jsonify({'following': False})
    else:
        follow = Follow(follower_id=session['user_id'], followed_id=user_id)
        db.session.add(follow)
        User.query.get(session['user_id']).following += 1
        User.query.get(user_id).followers += 1
        db.session.commit()
        return jsonify({'following': True})

@app.route('/api/follow/status/<int:user_id>')
def follow_status(user_id):
    if not session.get('user_id'):
        return jsonify({'status': 'none'})
    following = Follow.query.filter_by(follower_id=session['user_id'], followed_id=user_id).first()
    return jsonify({'status': 'following' if following else 'none'})

# ==================== UPLOAD ROUTES ====================
@app.route('/upload/video', methods=['POST'])
def upload_video():
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'video' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['video']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file.save(os.path.join('static/uploads/videos', unique_filename))
        
        video = Video(
            user_id=session['user_id'],
            title=request.form.get('title', 'New Video'),
            filename=unique_filename,
            file_path=f'/static/uploads/videos/{unique_filename}',
            video_type='video'
        )
        db.session.add(video)
        db.session.commit()
        socketio.emit('new_video', video.to_dict())
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/upload/reel', methods=['POST'])
def upload_reel():
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'reel' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['reel']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file.save(os.path.join('static/uploads/reels', unique_filename))
        
        reel = Video(
            user_id=session['user_id'],
            title=request.form.get('title', 'New Reel'),
            filename=unique_filename,
            file_path=f'/static/uploads/reels/{unique_filename}',
            video_type='reel',
            music=request.form.get('music', 'Original Audio')
        )
        db.session.add(reel)
        db.session.commit()
        socketio.emit('new_reel', reel.to_dict())
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/upload/story', methods=['POST'])
def upload_story():
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'story' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['story']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file.save(os.path.join('static/uploads/stories', unique_filename))
        
        story = Story(
            user_id=session['user_id'],
            filename=unique_filename,
            file_path=f'/static/uploads/stories/{unique_filename}'
        )
        db.session.add(story)
        db.session.commit()
        socketio.emit('new_story', story.to_dict())
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid file'}), 400

# ==================== API ROUTES ====================
@app.route('/api/videos')
def get_videos():
    videos = Video.query.filter_by(video_type='video').order_by(Video.created_at.desc()).all()
    return jsonify([v.to_dict() for v in videos])

@app.route('/api/reels')
def get_reels():
    reels = Video.query.filter_by(video_type='reel').order_by(Video.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reels])

@app.route('/api/stories')
def get_stories():
    stories = Story.query.filter(Story.expires_at > datetime.utcnow()).order_by(Story.created_at.desc()).all()
    return jsonify([s.to_dict() for s in stories])

@app.route('/api/profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    
    videos = Video.query.filter_by(user_id=user_id).count()
    return jsonify({
        'id': user.id,
        'username': user.username,
        'name': user.full_name,
        'pic': user.profile_pic,
        'bio': user.bio,
        'followers': user.followers,
        'following': user.following,
        'posts': videos
    })

@app.route('/api/user-videos/<int:user_id>')
def get_user_videos(user_id):
    videos = Video.query.filter_by(user_id=user_id).order_by(Video.created_at.desc()).all()
    return jsonify([{'id': v.id, 'file_path': v.file_path, 'video_type': v.video_type, 'title': v.title} for v in videos])

# ==================== CHAT ROUTES ====================
@app.route('/api/chat/users')
def get_chat_users():
    if not session.get('user_id'):
        return jsonify([])
    
    following = [f.followed_id for f in Follow.query.filter_by(follower_id=session['user_id']).all()]
    followers = [f.follower_id for f in Follow.query.filter_by(followed_id=session['user_id']).all()]
    connected = set(following) & set(followers)
    
    users = User.query.filter(User.id.in_(connected) if connected else User.id == -1).all()
    
    result = []
    for u in users:
        last_msg = Message.query.filter(
            ((Message.sender_id == session['user_id']) & (Message.receiver_id == u.id)) |
            ((Message.sender_id == u.id) & (Message.receiver_id == session['user_id']))
        ).order_by(Message.created_at.desc()).first()
        
        unread = Message.query.filter_by(sender_id=u.id, receiver_id=session['user_id'], is_read=False).count()
        
        result.append({
            'id': u.id,
            'name': u.full_name,
            'pic': u.profile_pic,
            'online': u.online,
            'last_msg': last_msg.content if last_msg else 'Start conversation',
            'unread': unread
        })
    return jsonify(result)

@app.route('/api/messages/<int:other_id>')
def get_messages(other_id):
    if not session.get('user_id'):
        return jsonify([])
    
    messages = Message.query.filter(
        ((Message.sender_id == session['user_id']) & (Message.receiver_id == other_id)) |
        ((Message.sender_id == other_id) & (Message.receiver_id == session['user_id']))
    ).order_by(Message.created_at).all()
    
    Message.query.filter_by(sender_id=other_id, receiver_id=session['user_id'], is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify([{
        'sender_id': m.sender_id,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    } for m in messages])

# ==================== SOCKETIO EVENTS ====================
@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.online = True
            db.session.commit()
            join_room(f'user_{user_id}')
            emit('user_status', {'user_id': user_id, 'online': True}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.online = False
            db.session.commit()
            emit('user_status', {'user_id': user_id, 'online': False}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    sender_id = session.get('user_id')
    if not sender_id:
        return
    
    follow1 = Follow.query.filter_by(follower_id=sender_id, followed_id=data['receiver_id']).first()
    follow2 = Follow.query.filter_by(follower_id=data['receiver_id'], followed_id=sender_id).first()
    
    if not (follow1 and follow2):
        return
    
    msg = Message(sender_id=sender_id, receiver_id=data['receiver_id'], content=data['content'])
    db.session.add(msg)
    db.session.commit()
    
    sender = User.query.get(sender_id)
    message_data = {
        'sender_id': sender_id,
        'sender_name': sender.full_name,
        'sender_pic': sender.profile_pic,
        'content': data['content'],
        'created_at': msg.created_at.isoformat()
    }
    
    emit('new_message', message_data, room=f'user_{data["receiver_id"]}')
    emit('new_message', message_data, room=f'user_{sender_id}')

@socketio.on('join')
def handle_join(data):
    if 'user_id' in data:
        join_room(f'user_{data["user_id"]}')

# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Connectify</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background: #fafafa; }
        
        .auth-page { height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .auth-card { background: white; padding: 40px 30px; width: 400px; border-radius: 20px; box-shadow: 0 15px 40px rgba(0,0,0,0.2); }
        .auth-card h2 { color: #333; margin-bottom: 20px; font-size: 32px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .tab-container { display: flex; margin-bottom: 20px; border-bottom: 2px solid #eee; }
        .auth-tab { flex: 1; text-align: center; padding: 10px; cursor: pointer; color: #999; background: none; border: none; font-size: 16px; }
        .auth-tab.active { color: #667eea; border-bottom: 2px solid #667eea; }
        .auth-form { display: none; }
        .auth-form.active { display: block; }
        .auth-form input, .auth-form textarea { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; }
        .auth-btn { width: 100%; padding: 12px; border: none; border-radius: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 16px; cursor: pointer; font-weight: 600; }
        
        .app { display: none; }
        .sidebar { width: 250px; height: 100vh; background: white; border-right: 1px solid #dbdbdb; position: fixed; left: 0; top: 0; padding: 20px; }
        .sidebar .logo { font-size: 24px; font-weight: bold; margin-bottom: 30px; color: #667eea; }
        .sidebar ul { list-style: none; }
        .sidebar li { padding: 15px; margin: 5px 0; border-radius: 10px; cursor: pointer; display: flex; align-items: center; gap: 10px; }
        .sidebar li:hover { background: #f5f5f5; }
        .sidebar li.active { background: #f0f2f5; }
        .sidebar li.delete { color: #ff4444; }
        .main { margin-left: 250px; padding: 20px; }
        
        .feed { max-width: 800px; margin: 0 auto; }
        .post { background: white; border-radius: 12px; border: 1px solid #dbdbdb; margin-bottom: 30px; }
        .post-header { padding: 15px; display: flex; align-items: center; gap: 10px; }
        .post-header img { width: 40px; height: 40px; border-radius: 50%; }
        .video-container video { width: 100%; max-height: 500px; }
        
        .reels-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
        .reel { background: white; border-radius: 12px; overflow: hidden; }
        .reel-media { aspect-ratio: 9/16; background: black; }
        .reel-media video { width: 100%; height: 100%; object-fit: cover; }
        
        .chat-container { background: white; border-radius: 12px; height: 70vh; display: flex; flex-direction: column; }
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; }
        .message { max-width: 70%; padding: 10px 15px; border-radius: 18px; margin: 5px 0; }
        .message.sent { align-self: flex-end; background: #667eea; color: white; margin-left: auto; }
        .message.received { align-self: flex-start; background: #f0f2f5; }
        .chat-input { display: flex; padding: 15px; gap: 10px; }
        .chat-input input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; }
        .chat-input button { background: #667eea; color: white; border: none; width: 45px; height: 45px; border-radius: 50%; cursor: pointer; }
        
        .profile-header { background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; }
        .profile-info { display: flex; gap: 50px; }
        .profile-stats { display: flex; gap: 40px; margin: 20px 0; }
        .follow-btn { background: #667eea; color: white; border: none; padding: 8px 20px; border-radius: 5px; cursor: pointer; }
        .follow-btn.following { background: #dbdbdb; color: #262626; }
        
        .create-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 2000; }
        .create-modal-content { background: white; border-radius: 20px; width: 400px; padding: 20px; }
        
        .chat-list { background: white; border-radius: 12px; }
        .chat-item { display: flex; align-items: center; gap: 15px; padding: 15px; border-bottom: 1px solid #eee; cursor: pointer; }
        .chat-item:hover { background: #f5f5f5; }
        .chat-item img { width: 50px; height: 50px; border-radius: 50%; }
        .unread-badge { background: #667eea; color: white; border-radius: 50%; padding: 5px 10px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="auth-page" id="auth">
        <div class="auth-card">
            <h2>Connectify</h2>
            <div class="tab-container">
                <button class="auth-tab active" onclick="switchTab('login')">LOGIN</button>
                <button class="auth-tab" onclick="switchTab('register')">REGISTER</button>
            </div>
            <div class="auth-form active" id="login-form">
                <input type="text" id="login-username" placeholder="Username">
                <input type="password" id="login-password" placeholder="Password">
                <button class="auth-btn" onclick="login()">Log In</button>
            </div>
            <div class="auth-form" id="register-form">
                <input type="text" id="reg-username" placeholder="Username" required>
                <input type="password" id="reg-password" placeholder="Password" required>
                <input type="text" id="reg-fullname" placeholder="Full Name">
                <textarea id="reg-bio" placeholder="Bio"></textarea>
                <button class="auth-btn" onclick="register()">Create Account</button>
            </div>
        </div>
    </div>

    <div class="app" id="app">
        <div class="sidebar">
            <div class="logo">Connectify</div>
            <ul>
                <li onclick="showPage('home')" class="active" id="menu-home"><i class="fas fa-home"></i> Home</li>
                <li onclick="showPage('reels')" id="menu-reels"><i class="fas fa-film"></i> Reels</li>
                <li onclick="showPage('chat')" id="menu-chat"><i class="fas fa-paper-plane"></i> Messages</li>
                <li onclick="showPage('profile')" id="menu-profile"><i class="fas fa-user"></i> Profile</li>
                <li onclick="openCreateModal()"><i class="fas fa-plus-circle"></i> Create</li>
                <li onclick="showDeleteConfirm()" style="color: #ff4444;"><i class="fas fa-trash-alt"></i> Delete Account</li>
                <li onclick="logout()" style="color: #ed4956;"><i class="fas fa-sign-out-alt"></i> Logout</li>
            </ul>
        </div>
        <div class="main" id="main"></div>
    </div>

    <div class="create-modal" id="createModal">
        <div class="create-modal-content">
            <h3 style="margin-bottom: 20px;">Create New</h3>
            <div onclick="uploadFile('video')" style="padding: 15px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 10px; cursor: pointer;">
                <i class="fas fa-video"></i> Upload Video
            </div>
            <div onclick="uploadFile('reel')" style="padding: 15px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 10px; cursor: pointer;">
                <i class="fas fa-film"></i> Upload Reel
            </div>
            <div onclick="uploadFile('story')" style="padding: 15px; border: 1px solid #ddd; border-radius: 10px; cursor: pointer;">
                <i class="fas fa-clock"></i> Add Story
            </div>
            <button onclick="closeCreateModal()" style="margin-top: 20px; width: 100%; padding: 10px;">Close</button>
        </div>
    </div>

    <input type="file" id="fileInput" style="display: none;" accept="video/*">

    <script>
        let currentUser = null;
        let socket = null;
        let currentChatUser = null;

        function switchTab(tab) {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            
            if (tab === 'login') {
                document.querySelectorAll('.auth-tab')[0].classList.add('active');
                document.getElementById('login-form').classList.add('active');
            } else {
                document.querySelectorAll('.auth-tab')[1].classList.add('active');
                document.getElementById('register-form').classList.add('active');
            }
        }

        async function register() {
            const data = {
                username: document.getElementById('reg-username').value,
                password: document.getElementById('reg-password').value,
                full_name: document.getElementById('reg-fullname').value,
                bio: document.getElementById('reg-bio').value
            };
            
            try {
                const res = await fetch('/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                
                if (result.success) {
                    currentUser = result.user;
                    document.getElementById('auth').style.display = 'none';
                    document.getElementById('app').style.display = 'block';
                    connectSocket();
                    showPage('home');
                } else {
                    alert('Registration failed: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error connecting to server');
            }
        }

        async function login() {
            const data = {
                username: document.getElementById('login-username').value,
                password: document.getElementById('login-password').value
            };
            
            try {
                const res = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                
                if (result.success) {
                    currentUser = result.user;
                    document.getElementById('auth').style.display = 'none';
                    document.getElementById('app').style.display = 'block';
                    connectSocket();
                    showPage('home');
                } else {
                    alert('Login failed');
                }
            } catch (error) {
                alert('Error connecting to server');
            }
        }

        function connectSocket() {
            socket = io();
            socket.on('user_status', updateUserStatus);
            socket.on('new_message', handleNewMessage);
            socket.emit('join', {user_id: currentUser.id});
        }

        async function logout() {
            await fetch('/logout');
            if (socket) socket.disconnect();
            document.getElementById('app').style.display = 'none';
            document.getElementById('auth').style.display = 'flex';
        }

        function showDeleteConfirm() {
            if (confirm('Are you sure you want to delete your account? This cannot be undone!')) {
                deleteAccount();
            }
        }

        async function deleteAccount() {
            try {
                const res = await fetch('/delete-account', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const data = await res.json();
                
                if (data.success) {
                    alert('Account deleted successfully');
                    if (socket) socket.disconnect();
                    document.getElementById('app').style.display = 'none';
                    document.getElementById('auth').style.display = 'block';
                    document.getElementById('login-username').value = '';
                    document.getElementById('login-password').value = '';
                } else {
                    alert('Error deleting account: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error connecting to server');
            }
        }

        function showPage(page) {
            document.querySelectorAll('.sidebar li').forEach(l => l.classList.remove('active'));
            document.getElementById(`menu-${page}`).classList.add('active');
            
            if (page === 'home') loadHome();
            else if (page === 'reels') loadReels();
            else if (page === 'chat') loadChatList();
            else if (page === 'profile') loadProfile(currentUser.id);
        }

        async function loadHome() {
            try {
                const res = await fetch('/api/videos');
                const videos = await res.json();
                
                let html = '<div class="feed">';
                if (videos.length === 0) {
                    html += '<p style="text-align: center; padding: 50px;">No videos yet. Be the first to upload!</p>';
                } else {
                    videos.forEach(v => {
                        html += `
                            <div class="post">
                                <div class="post-header">
                                    <img src="${v.profile_pic}">
                                    <div><strong>${v.full_name}</strong></div>
                                </div>
                                <div class="video-container">
                                    <video src="${v.file_path}" controls></video>
                                </div>
                                <div style="padding: 15px;">
                                    <strong>${v.username}</strong> ${v.title}<br>
                                    <small>❤️ ${v.likes} likes • 👁️ ${v.views} views</small>
                                </div>
                            </div>
                        `;
                    });
                }
                html += '</div>';
                document.getElementById('main').innerHTML = html;
            } catch (error) {
                console.error('Error loading home:', error);
            }
        }

        async function loadReels() {
            try {
                const res = await fetch('/api/reels');
                const reels = await res.json();
                
                let html = '<div class="reels-grid">';
                if (reels.length === 0) {
                    html = '<p style="text-align: center; padding: 50px;">No reels yet. Create your first reel!</p>';
                } else {
                    reels.forEach(r => {
                        html += `
                            <div class="reel">
                                <div class="reel-media">
                                    <video src="${r.file_path}" loop muted></video>
                                </div>
                                <div style="padding: 10px;">
                                    <img src="${r.profile_pic}" style="width: 30px; height: 30px; border-radius: 50%;"> ${r.full_name}<br>
                                    <small>❤️ ${r.likes} • 🎵 ${r.music}</small>
                                </div>
                            </div>
                        `;
                    });
                }
                html += '</div>';
                document.getElementById('main').innerHTML = html;
            } catch (error) {
                console.error('Error loading reels:', error);
            }
        }

        async function loadChatList() {
            try {
                const res = await fetch('/api/chat/users');
                const users = await res.json();
                
                let html = '<h3>Messages</h3><div class="chat-list">';
                if (users.length === 0) {
                    html += '<p style="padding: 20px;">Follow someone to start chatting!</p>';
                } else {
                    users.forEach(u => {
                        html += `
                            <div class="chat-item" onclick="openChat(${u.id})">
                                <img src="${u.pic}">
                                <div style="flex:1">
                                    <strong>${u.name}</strong> ${u.online ? '<span style="color: #4CAF50;">●</span>' : ''}<br>
                                    <small>${u.last_msg}</small>
                                </div>
                                ${u.unread ? '<span class="unread-badge">' + u.unread + '</span>' : ''}
                            </div>
                        `;
                    });
                }
                html += '</div>';
                document.getElementById('main').innerHTML = html;
            } catch (error) {
                console.error('Error loading chat list:', error);
            }
        }

        async function openChat(userId) {
            try {
                const [usersRes, msgsRes] = await Promise.all([
                    fetch('/api/chat/users'),
                    fetch(`/api/messages/${userId}`)
                ]);
                const users = await usersRes.json();
                const messages = await msgsRes.json();
                const chatUser = users.find(u => u.id === userId);
                currentChatUser = chatUser;
                
                let html = `
                    <div class="chat-container">
                        <div style="padding: 15px; border-bottom: 1px solid #eee;">
                            <i class="fas fa-arrow-left" onclick="loadChatList()" style="cursor: pointer;"></i>
                            <img src="${chatUser.pic}" style="width: 40px; height: 40px; border-radius: 50%; margin-left: 10px;">
                            <strong>${chatUser.name}</strong>
                        </div>
                        <div class="chat-messages" id="chatMessages">
                `;
                
                messages.forEach(m => {
                    const sent = m.sender_id === currentUser.id;
                    html += `<div class="message ${sent ? 'sent' : 'received'}">${m.content}</div>`;
                });
                
                html += `
                        </div>
                        <div class="chat-input">
                            <input type="text" id="messageInput" placeholder="Message..." onkeypress="if(event.key==='Enter') sendMessage(${userId})">
                            <button onclick="sendMessage(${userId})"><i class="fas fa-paper-plane"></i></button>
                        </div>
                    </div>
                `;
                
                document.getElementById('main').innerHTML = html;
                setTimeout(() => {
                    const chat = document.getElementById('chatMessages');
                    if (chat) chat.scrollTop = chat.scrollHeight;
                }, 100);
            } catch (error) {
                console.error('Error opening chat:', error);
            }
        }

        function sendMessage(receiverId) {
            const input = document.getElementById('messageInput');
            if (!input.value.trim() || !socket) return;
            
            socket.emit('send_message', {
                receiver_id: receiverId,
                content: input.value
            });
            
            const chat = document.getElementById('chatMessages');
            chat.innerHTML += `<div class="message sent">${input.value}</div>`;
            chat.scrollTop = chat.scrollHeight;
            input.value = '';
        }

        function handleNewMessage(msg) {
            if (currentChatUser && (msg.sender_id === currentChatUser.id || msg.sender_id === currentUser.id)) {
                const chat = document.getElementById('chatMessages');
                if (chat && msg.sender_id !== currentUser.id) {
                    chat.innerHTML += `<div class="message received">${msg.content}</div>`;
                    chat.scrollTop = chat.scrollHeight;
                }
            }
        }

        function updateUserStatus(data) {
            if (currentChatUser && currentChatUser.id === data.user_id) {
                const status = document.querySelector('.chat-container small');
                if (status) status.innerHTML = data.online ? '● Online' : 'Offline';
            }
        }

        async function loadProfile(userId) {
            try {
                const [profileRes, videosRes] = await Promise.all([
                    fetch(`/api/profile/${userId}`),
                    fetch(`/api/user-videos/${userId}`)
                ]);
                const profile = await profileRes.json();
                const videos = await videosRes.json();
                
                let followBtn = '';
                if (userId !== currentUser.id) {
                    const statusRes = await fetch(`/api/follow/status/${userId}`);
                    const status = await statusRes.json();
                    followBtn = `<button class="follow-btn ${status.status === 'following' ? 'following' : ''}" onclick="toggleFollow(${userId})">
                        ${status.status === 'following' ? 'Following ✓' : 'Follow'}
                    </button>`;
                }
                
                let html = `
                    <div class="profile-header">
                        <div class="profile-info">
                            <img src="${profile.pic}" style="width: 150px; height: 150px; border-radius: 50%;">
                            <div>
                                <h2>${profile.username}</h2>
                                ${followBtn}
                                <div class="profile-stats">
                                    <div><strong>${profile.posts}</strong> posts</div>
                                    <div><strong>${profile.followers}</strong> followers</div>
                                    <div><strong>${profile.following}</strong> following</div>
                                </div>
                                <div><strong>${profile.name}</strong></div>
                                <div>${profile.bio}</div>
                            </div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3,1fr); gap: 5px;">
                `;
                
                videos.forEach(v => {
                    html += `<div style="aspect-ratio: 1; background: #f0f0f0;">
                        <video src="${v.file_path}" style="width: 100%; height: 100%; object-fit: cover;"></video>
                    </div>`;
                });
                
                html += '</div>';
                document.getElementById('main').innerHTML = html;
            } catch (error) {
                console.error('Error loading profile:', error);
            }
        }

        async function toggleFollow(userId) {
            try {
                const res = await fetch(`/api/follow/${userId}`, {method: 'POST'});
                await res.json();
                loadProfile(userId);
            } catch (error) {
                console.error('Error toggling follow:', error);
            }
        }

        function openCreateModal() {
            document.getElementById('createModal').style.display = 'flex';
        }

        function closeCreateModal() {
            document.getElementById('createModal').style.display = 'none';
        }

        function uploadFile(type) {
            closeCreateModal();
            const input = document.getElementById('fileInput');
            input.accept = 'video/*';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const title = prompt('Enter title:');
                if (!title) return;
                
                const formData = new FormData();
                formData.append(type, file);
                formData.append('title', title);
                if (type === 'reel') {
                    formData.append('music', prompt('Enter music name:', 'Original Audio') || 'Original Audio');
                }
                
                try {
                    const res = await fetch(`/upload/${type}`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (res.ok) {
                        alert('Upload successful!');
                        showPage('home');
                    } else {
                        alert('Upload failed');
                    }
                } catch (error) {
                    alert('Error uploading file');
                }
            };
            input.click();
        }
    </script>
</body>
</html>
'''

# ==================== HOME ROUTE ====================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
