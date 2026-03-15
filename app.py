# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///connectify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'm4v', 'jpg', 'jpeg', 'png', 'gif'}
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Create upload folders
os.makedirs('static/uploads/videos', exist_ok=True)
os.makedirs('static/uploads/reels', exist_ok=True)
os.makedirs('static/uploads/stories', exist_ok=True)
os.makedirs('static/uploads/profiles', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ==================== DATABASE MODELS ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(500), default='/static/default-profile.jpg')
    bio = db.Column(db.Text, default='')
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

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self, current_user_id=None):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'unknown',
            'user_pic': self.user.profile_pic if self.user else '',
            'content': self.content,
            'likes': self.likes,
            'user_liked': self.is_liked_by(current_user_id) if current_user_id else False,
            'replies_count': self.replies.count(),
            'created_at': self.created_at.isoformat()
        }
    
    def is_liked_by(self, user_id):
        if not user_id:
            return False
        return CommentLike.query.filter_by(user_id=user_id, comment_id=self.id).first() is not None

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='unique_comment_like'),)

# Create tables (NO DUMMY DATA)
with app.app_context():
    db.create_all()
    print("✅ Database tables created (No dummy data)")

# Create a default profile image if it doesn't exist
def create_default_profile():
    default_profile_path = 'static/default-profile.jpg'
    if not os.path.exists(default_profile_path):
        # You can create a simple colored placeholder or copy a default image
        # For now, we'll just note that it doesn't exist
        print("⚠️  Default profile image not found at static/default-profile.jpg")

create_default_profile()

# ==================== VIDEO SERVING ROUTE ====================
@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory('static/uploads', filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

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
        bio=data.get('bio', ''),
        profile_pic='/static/default-profile.jpg'
    )
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return jsonify({'success': True, 'user': {'id': user.id, 'name': user.full_name, 'pic': user.profile_pic, 'username': user.username, 'bio': user.bio}})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        user.online = True
        db.session.commit()
        socketio.emit('user_status', {'user_id': user.id, 'online': True})
        return jsonify({'success': True, 'user': {'id': user.id, 'name': user.full_name, 'pic': user.profile_pic, 'username': user.username, 'bio': user.bio}})
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
        
        # Delete profile picture if not default
        if user.profile_pic and user.profile_pic != '/static/default-profile.jpg':
            profile_path = os.path.join('static', user.profile_pic.replace('/static/', ''))
            if os.path.exists(profile_path):
                os.remove(profile_path)
        
        # Delete all user data from database
        Video.query.filter_by(user_id=user_id).delete()
        Story.query.filter_by(user_id=user_id).delete()
        Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).delete()
        Follow.query.filter((Follow.follower_id == user_id) | (Follow.followed_id == user_id)).delete()
        Comment.query.filter_by(user_id=user_id).delete()
        CommentLike.query.filter_by(user_id=user_id).delete()
        
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

# ==================== EDIT PROFILE ROUTES ====================
@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Handle form data (for multipart/form-data with file upload)
    if request.content_type and 'multipart/form-data' in request.content_type:
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        bio = request.form.get('bio')
        
        # Check if username is taken by another user
        if username and username != user.username:
            existing = User.query.filter_by(username=username).first()
            if existing:
                return jsonify({'error': 'Username already taken'}), 400
            user.username = username
        
        if full_name is not None:
            user.full_name = full_name
        if bio is not None:
            user.bio = bio
        
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                # Check if it's an image
                if file.content_type and file.content_type.startswith('image/'):
                    filename = secure_filename(file.filename)
                    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
                    unique_filename = f"profile_{user.id}_{uuid.uuid4().hex[:8]}.{ext}"
                    
                    file_path = os.path.join('static/uploads/profiles', unique_filename)
                    file.save(file_path)
                    
                    # Delete old profile picture if not default
                    if user.profile_pic and user.profile_pic != '/static/default-profile.jpg':
                        old_path = os.path.join('static', user.profile_pic.replace('/static/', ''))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    # Update user's profile picture
                    user.profile_pic = f'/static/uploads/profiles/{unique_filename}'
    
    # Handle JSON data (for password update etc)
    elif request.is_json:
        data = request.json
        if 'current_password' in data and 'new_password' in data:
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            if not check_password_hash(user.password, current_password):
                return jsonify({'error': 'Current password is incorrect'}), 400
            
            user.password = generate_password_hash(new_password)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'name': user.full_name,
            'pic': user.profile_pic,
            'bio': user.bio
        }
    })

# ==================== LIKE ROUTE ====================
@app.route('/api/like/<int:video_id>', methods=['POST'])
def like_video(video_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    video.likes += 1
    db.session.commit()
    
    socketio.emit('video_liked', {
        'video_id': video_id,
        'likes': video.likes,
        'user_id': session['user_id']
    })
    
    return jsonify({'success': True, 'likes': video.likes})

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

# ==================== FOLLOWERS/FOLLOWING LIST ROUTES ====================
@app.route('/api/followers/<int:user_id>')
def get_followers(user_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    followers = Follow.query.filter_by(followed_id=user_id).all()
    follower_users = []
    for follow in followers:
        user = User.query.get(follow.follower_id)
        if user:
            # Check if current user follows this follower
            is_following = Follow.query.filter_by(
                follower_id=session['user_id'], 
                followed_id=user.id
            ).first() is not None
            
            follower_users.append({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'profile_pic': user.profile_pic,
                'bio': user.bio,
                'is_following': is_following,
                'is_current_user': user.id == session['user_id']
            })
    
    return jsonify(follower_users)

@app.route('/api/following/<int:user_id>')
def get_following(user_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    following = Follow.query.filter_by(follower_id=user_id).all()
    following_users = []
    for follow in following:
        user = User.query.get(follow.followed_id)
        if user:
            # Check if current user follows this user
            is_following = Follow.query.filter_by(
                follower_id=session['user_id'], 
                followed_id=user.id
            ).first() is not None
            
            following_users.append({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'profile_pic': user.profile_pic,
                'bio': user.bio,
                'is_following': is_following,
                'is_current_user': user.id == session['user_id']
            })
    
    return jsonify(following_users)

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

# ==================== COMMENT ROUTES ====================
@app.route('/api/comments/<int:video_id>', methods=['GET'])
def get_comments(video_id):
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    comments = Comment.query.filter_by(video_id=video_id, parent_id=None)\
        .order_by(Comment.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    current_user_id = session.get('user_id')
    result = [c.to_dict(current_user_id) for c in comments.items]
    
    return jsonify({
        'comments': result,
        'has_next': comments.has_next,
        'page': page
    })

@app.route('/api/comments/<int:comment_id>/replies', methods=['GET'])
def get_comment_replies(comment_id):
    replies = Comment.query.filter_by(parent_id=comment_id)\
        .order_by(Comment.created_at.asc()).all()
    
    current_user_id = session.get('user_id')
    result = [r.to_dict(current_user_id) for r in replies]
    
    return jsonify(result)

@app.route('/api/comment', methods=['POST'])
def add_comment():
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    video_id = data.get('video_id')
    content = data.get('content')
    parent_id = data.get('parent_id')
    
    if not video_id or not content:
        return jsonify({'error': 'Missing data'}), 400
    
    comment = Comment(
        user_id=session['user_id'],
        video_id=video_id,
        parent_id=parent_id,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    comment_data = comment.to_dict(session['user_id'])
    
    if parent_id:
        socketio.emit('new_reply', {
            'parent_id': parent_id,
            'comment': comment_data
        })
    else:
        socketio.emit('new_comment', {
            'video_id': video_id,
            'comment': comment_data
        })
    
    return jsonify({'success': True, 'comment_id': comment.id})

@app.route('/api/comment/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    existing_like = CommentLike.query.filter_by(
        user_id=session['user_id'],
        comment_id=comment_id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        comment.likes -= 1
        liked = False
    else:
        like = CommentLike(user_id=session['user_id'], comment_id=comment_id)
        db.session.add(like)
        comment.likes += 1
        liked = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'likes': comment.likes,
        'liked': liked
    })

@app.route('/api/comment/<int:comment_id>/delete', methods=['DELETE'])
def delete_comment(comment_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Not logged in'}), 401
    
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    if comment.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    CommentLike.query.filter_by(comment_id=comment_id).delete()
    Comment.query.filter_by(parent_id=comment_id).delete()
    db.session.delete(comment)
    db.session.commit()
    
    socketio.emit('comment_deleted', {
        'comment_id': comment_id,
        'video_id': comment.video_id
    })
    
    return jsonify({'success': True})

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
        .post { background: white; border-radius: 12px; border: 1px solid #dbdbdb; margin-bottom: 30px; overflow: hidden; }
        .post-header { padding: 15px; display: flex; align-items: center; gap: 10px; }
        .post-header img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
        
        .video-container { 
            width: 100%; 
            background: black; 
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
        }
        .video-container video { 
            width: auto;
            height: auto;
            max-width: 100%;
            max-height: 500px;
            object-fit: scale-down;
            background: black;
        }
        
        .post-actions {
            padding: 15px;
            display: flex;
            gap: 20px;
        }
        .post-actions i {
            font-size: 26px;
            cursor: pointer;
        }
        .post-actions i.fas.fa-heart {
            color: #ed4956;
        }
        .fa-bookmark { margin-left: auto; }
        
        .post-likes {
            padding: 0 15px 8px;
            font-weight: bold;
        }
        .post-caption {
            padding: 0 15px 15px;
        }
        
        .comments-section {
            padding: 15px;
            border-top: 1px solid #eee;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .comment {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .comment-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            object-fit: cover;
        }
        
        .comment-content {
            flex: 1;
        }
        
        .comment-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 5px;
        }
        
        .comment-username {
            font-weight: 600;
            font-size: 14px;
        }
        
        .comment-time {
            font-size: 12px;
            color: #999;
        }
        
        .comment-text {
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .comment-actions {
            display: flex;
            gap: 15px;
            font-size: 12px;
            color: #999;
        }
        
        .comment-action {
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .comment-action:hover {
            color: #667eea;
        }
        
        .comment-action.liked {
            color: #ed4956;
        }
        
        .comment-action.liked i {
            font-weight: 900;
        }
        
        .reply-section {
            margin-left: 42px;
            margin-top: 10px;
            padding-left: 10px;
            border-left: 2px solid #eee;
        }
        
        .reply-input {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .reply-input input {
            flex: 1;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 14px;
        }
        
        .reply-input button {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
        }
        
        .view-replies {
            color: #667eea;
            cursor: pointer;
            font-size: 12px;
            margin-top: 5px;
        }
        
        .reels-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
        .reel { background: white; border-radius: 12px; overflow: hidden; }
        .reel-media { 
            aspect-ratio: 9/16; 
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .reel-media video { 
            width: auto;
            height: auto;
            max-width: 100%;
            max-height: 100%;
            object-fit: scale-down;
            background: black;
        }
        
        .chat-container { background: white; border-radius: 12px; height: 70vh; display: flex; flex-direction: column; }
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; }
        .message { max-width: 70%; padding: 10px 15px; border-radius: 18px; margin: 5px 0; }
        .message.sent { align-self: flex-end; background: #667eea; color: white; }
        .message.received { align-self: flex-start; background: #f0f2f5; }
        .chat-input { display: flex; padding: 15px; gap: 10px; }
        .chat-input input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; }
        .chat-input button { background: #667eea; color: white; border: none; width: 45px; height: 45px; border-radius: 50%; cursor: pointer; }
        
        .profile-header { background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; }
        .profile-info { display: flex; gap: 50px; }
        .profile-stats { display: flex; gap: 40px; margin: 20px 0; }
        .stat-item {
            text-align: center;
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 10px;
            transition: background-color 0.3s;
        }
        .stat-item:hover {
            background-color: #f0f0f0;
        }
        .stat-number {
            font-size: 18px;
            font-weight: 600;
        }
        .stat-label {
            font-size: 14px;
            color: #8e8e8e;
        }
        .edit-profile-btn { 
            background: #0095f6; 
            color: white; 
            border: none; 
            padding: 8px 20px; 
            border-radius: 8px; 
            cursor: pointer;
            font-weight: 600;
            margin-left: 20px;
        }
        .follow-btn { background: #667eea; color: white; border: none; padding: 8px 20px; border-radius: 5px; cursor: pointer; }
        .follow-btn.following { background: #dbdbdb; color: #262626; }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            background-color: white;
            width: 400px;
            max-width: 90%;
            max-height: 80vh;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .modal-header {
            padding: 16px;
            border-bottom: 1px solid #dbdbdb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-header h3 {
            margin: 0;
            font-size: 16px;
        }
        .modal-close {
            cursor: pointer;
            font-size: 20px;
        }
        .modal-body {
            padding: 16px;
            overflow-y: auto;
            flex: 1;
        }
        .modal-search {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #dbdbdb;
            border-radius: 8px;
            margin-bottom: 16px;
            font-size: 14px;
        }
        .user-list-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px;
            border-bottom: 1px solid #f0f0f0;
        }
        .user-list-item img {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            object-fit: cover;
        }
        .user-list-info {
            flex: 1;
        }
        .user-list-username {
            font-weight: 600;
            font-size: 14px;
        }
        .user-list-name {
            font-size: 12px;
            color: #8e8e8e;
        }
        .user-list-follow-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 6px 16px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
        }
        .user-list-follow-btn.following {
            background: #dbdbdb;
            color: #262626;
        }
        .user-list-follow-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .create-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 2000; }
        .create-modal-content { background: white; border-radius: 20px; width: 400px; padding: 20px; }
        
        .chat-list { background: white; border-radius: 12px; }
        .chat-item { display: flex; align-items: center; gap: 15px; padding: 15px; border-bottom: 1px solid #eee; cursor: pointer; }
        .chat-item:hover { background: #f5f5f5; }
        .chat-item img { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; }
        .unread-badge { background: #667eea; color: white; border-radius: 50%; padding: 5px 10px; font-size: 12px; }
        
        .profile-posts {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 5px;
            margin-top: 5px;
        }
        .profile-post {
            aspect-ratio: 1;
            background: #f0f0f0;
            overflow: hidden;
        }
        .profile-post video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .main { margin-left: 0; }
            .profile-info { flex-direction: column; gap: 20px; }
            .profile-stats { gap: 20px; }
            .reels-grid { grid-template-columns: repeat(2,1fr); gap: 10px; }
        }
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

    <!-- Followers Modal -->
    <div class="modal" id="followersModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Followers</h3>
                <span class="modal-close" onclick="closeFollowersModal()">&times;</span>
            </div>
            <div class="modal-body">
                <input type="text" class="modal-search" id="followersSearch" placeholder="Search" onkeyup="searchFollowers()">
                <div id="followersList"></div>
            </div>
        </div>
    </div>

    <!-- Following Modal -->
    <div class="modal" id="followingModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Following</h3>
                <span class="modal-close" onclick="closeFollowingModal()">&times;</span>
            </div>
            <div class="modal-body">
                <input type="text" class="modal-search" id="followingSearch" placeholder="Search" onkeyup="searchFollowing()">
                <div id="followingList"></div>
            </div>
        </div>
    </div>

    <!-- Edit Profile Modal -->
    <div class="modal" id="editProfileModal">
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3>Edit Profile</h3>
                <span class="modal-close" onclick="closeEditProfileModal()">&times;</span>
            </div>
            <div class="modal-body">
                <form id="editProfileForm" onsubmit="updateProfile(event)">
                    <!-- Profile Picture Section -->
                    <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <img id="editProfilePic" src="" style="width: 80px; height: 80px; border-radius: 50%; margin-right: 20px; object-fit: cover;">
                        <div>
                            <label for="profilePicInput" style="background: #667eea; color: white; padding: 8px 16px; border-radius: 5px; cursor: pointer; display: inline-block;">
                                <i class="fas fa-camera"></i> Change Photo
                            </label>
                            <input type="file" id="profilePicInput" accept="image/*" style="display: none;" onchange="previewProfilePic(this)">
                            <p style="font-size: 12px; color: #999; margin-top: 5px;">JPG or PNG</p>
                        </div>
                    </div>
                    
                    <!-- Username -->
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">Username</label>
                        <input type="text" id="editUsername" name="username" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;" required>
                    </div>
                    
                    <!-- Full Name -->
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">Full Name</label>
                        <input type="text" id="editFullName" name="full_name" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;">
                    </div>
                    
                    <!-- Bio -->
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">Bio</label>
                        <textarea id="editBio" name="bio" rows="4" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; resize: none;" maxlength="150" oninput="updateBioCount()"></textarea>
                        <div style="text-align: right; font-size: 12px; color: #999;">
                            <span id="bioCount">0</span>/150
                        </div>
                    </div>
                    
                    <!-- Change Password Link -->
                    <div style="text-align: right; margin-bottom: 15px;">
                        <a href="#" onclick="openPasswordModal(); return false;" style="color: #667eea; text-decoration: none; font-size: 14px;">
                            <i class="fas fa-key"></i> Change Password
                        </a>
                    </div>
                    
                    <!-- Submit Buttons -->
                    <div style="display: flex; gap: 10px;">
                        <button type="button" onclick="closeEditProfileModal()" style="flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; background: white; cursor: pointer;">Cancel</button>
                        <button type="submit" style="flex: 1; padding: 12px; border: none; border-radius: 8px; background: #667eea; color: white; cursor: pointer; font-weight: 600;">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Change Password Modal -->
    <div class="modal" id="passwordModal">
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <h3>Change Password</h3>
                <span class="modal-close" onclick="closePasswordModal()">&times;</span>
            </div>
            <div class="modal-body">
                <form id="passwordForm" onsubmit="updatePassword(event)">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">Current Password</label>
                        <input type="password" id="currentPassword" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;" required>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">New Password</label>
                        <input type="password" id="newPassword" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;" required minlength="6">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">Confirm New Password</label>
                        <input type="password" id="confirmPassword" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;" required minlength="6">
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        <button type="button" onclick="closePasswordModal()" style="flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; background: white; cursor: pointer;">Cancel</button>
                        <button type="submit" style="flex: 1; padding: 12px; border: none; border-radius: 8px; background: #667eea; color: white; cursor: pointer; font-weight: 600;">Update Password</button>
                    </div>
                </form>
            </div>
        </div>
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
        let currentVideoId = null;
        let currentProfileUserId = null;
        let followersData = [];
        let followingData = [];
        
        const BASE_URL = window.location.origin;

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
                const res = await fetch(BASE_URL + '/register', {
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
                alert('Error connecting to server: ' + error);
            }
        }

        async function login() {
            const data = {
                username: document.getElementById('login-username').value,
                password: document.getElementById('login-password').value
            };
            
            try {
                const res = await fetch(BASE_URL + '/login', {
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
                    alert('Login failed - Check username/password');
                }
            } catch (error) {
                alert('Error connecting to server: ' + error);
            }
        }

        function connectSocket() {
            socket = io(BASE_URL);
            socket.on('user_status', updateUserStatus);
            socket.on('new_message', handleNewMessage);
            socket.on('new_comment', handleNewComment);
            socket.on('new_reply', handleNewReply);
            socket.emit('join', {user_id: currentUser.id});
        }

        async function logout() {
            await fetch(BASE_URL + '/logout');
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
                const res = await fetch(BASE_URL + '/delete-account', {
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

        // ==================== EDIT PROFILE FUNCTIONS ====================
        function openEditProfileModal() {
            document.getElementById('editProfilePic').src = currentUser.pic;
            document.getElementById('editUsername').value = currentUser.username;
            document.getElementById('editFullName').value = currentUser.name || '';
            document.getElementById('editBio').value = currentUser.bio || '';
            document.getElementById('bioCount').textContent = (currentUser.bio || '').length;
            document.getElementById('editProfileModal').classList.add('active');
        }

        function closeEditProfileModal() {
            document.getElementById('editProfileModal').classList.remove('active');
        }

        function openPasswordModal() {
            closeEditProfileModal();
            document.getElementById('passwordModal').classList.add('active');
        }

        function closePasswordModal() {
            document.getElementById('passwordModal').classList.remove('active');
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmPassword').value = '';
        }

        function previewProfilePic(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('editProfilePic').src = e.target.result;
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function updateBioCount() {
            const bio = document.getElementById('editBio').value;
            document.getElementById('bioCount').textContent = bio.length;
        }

        async function updateProfile(event) {
            event.preventDefault();
            
            const formData = new FormData();
            formData.append('username', document.getElementById('editUsername').value);
            formData.append('full_name', document.getElementById('editFullName').value);
            formData.append('bio', document.getElementById('editBio').value);
            
            const fileInput = document.getElementById('profilePicInput');
            if (fileInput.files.length > 0) {
                formData.append('profile_pic', fileInput.files[0]);
            }
            
            try {
                const res = await fetch(BASE_URL + '/api/update-profile', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await res.json();
                
                if (data.success) {
                    currentUser = data.user;
                    closeEditProfileModal();
                    loadProfile(currentUser.id);
                    alert('Profile updated successfully!');
                } else {
                    alert('Error: ' + (data.error || 'Failed to update profile'));
                }
            } catch (error) {
                alert('Error updating profile: ' + error);
            }
        }

        async function updatePassword(event) {
            event.preventDefault();
            
            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (newPassword !== confirmPassword) {
                alert('New passwords do not match!');
                return;
            }
            
            if (newPassword.length < 6) {
                alert('Password must be at least 6 characters long');
                return;
            }
            
            try {
                const res = await fetch(BASE_URL + '/api/update-profile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        current_password: currentPassword,
                        new_password: newPassword
                    })
                });
                
                const data = await res.json();
                
                if (data.success) {
                    closePasswordModal();
                    alert('Password updated successfully!');
                } else {
                    alert('Error: ' + (data.error || 'Failed to update password'));
                }
            } catch (error) {
                alert('Error updating password: ' + error);
            }
        }

        // ==================== LIKE FUNCTIONS ====================
        async function likeVideo(videoId, element) {
            try {
                const res = await fetch(BASE_URL + '/api/like/' + videoId, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await res.json();
                if (data.success) {
                    element.classList.toggle('far');
                    element.classList.toggle('fas');
                    const likeSpan = element.closest('.post-actions').nextElementSibling;
                    if (likeSpan && likeSpan.classList.contains('post-likes')) {
                        likeSpan.innerText = data.likes + ' likes';
                    }
                }
            } catch (error) {
                console.error('Error liking video:', error);
            }
        }

        // ==================== COMMENT FUNCTIONS ====================
        async function loadComments(videoId, containerId, page = 1) {
            try {
                const res = await fetch(BASE_URL + `/api/comments/${videoId}?page=${page}`);
                const data = await res.json();
                
                let html = '';
                data.comments.forEach(c => {
                    html += renderComment(c);
                });
                
                if (data.has_next) {
                    html += `<div class="load-more-comments" onclick="loadComments(${videoId}, '${containerId}', ${page + 1})" style="text-align:center; padding:10px; color:#667eea; cursor:pointer;">Load more comments...</div>`;
                }
                
                document.getElementById(containerId).innerHTML = html;
            } catch (error) {
                console.error('Error loading comments:', error);
            }
        }

        function renderComment(c) {
            const timeAgo = getTimeAgo(c.created_at);
            const likedClass = c.user_liked ? 'liked' : '';
            const heartIcon = c.user_liked ? 'fas' : 'far';
            
            return `
                <div class="comment" id="comment-${c.id}">
                    <img src="${c.user_pic}" class="comment-avatar">
                    <div class="comment-content">
                        <div class="comment-header">
                            <span class="comment-username">${c.username}</span>
                            <span class="comment-time">${timeAgo}</span>
                        </div>
                        <div class="comment-text">${c.content}</div>
                        <div class="comment-actions">
                            <span class="comment-action ${likedClass}" onclick="likeComment(${c.id}, this)">
                                <i class="${heartIcon} fa-heart"></i> ${c.likes}
                            </span>
                            <span class="comment-action" onclick="showReplyInput(${c.id})">
                                <i class="far fa-comment"></i> Reply
                            </span>
                            ${c.user_id === currentUser.id ? `
                                <span class="comment-action" onclick="deleteComment(${c.id})">
                                    <i class="far fa-trash-alt"></i> Delete
                                </span>
                            ` : ''}
                        </div>
                        <div class="reply-section" id="replies-${c.id}"></div>
                        ${c.replies_count > 0 ? `
                            <div class="view-replies" onclick="loadReplies(${c.id})">
                                View ${c.replies_count} ${c.replies_count === 1 ? 'reply' : 'replies'} ▼
                            </div>
                        ` : ''}
                        <div class="reply-input" id="reply-input-${c.id}" style="display:none;">
                            <input type="text" placeholder="Write a reply..." id="reply-text-${c.id}">
                            <button onclick="addReply(${c.id})">Post</button>
                        </div>
                    </div>
                </div>
            `;
        }

        async function loadReplies(commentId) {
            try {
                const res = await fetch(BASE_URL + `/api/comments/${commentId}/replies`);
                const replies = await res.json();
                
                let html = '';
                replies.forEach(r => {
                    const timeAgo = getTimeAgo(r.created_at);
                    const likedClass = r.user_liked ? 'liked' : '';
                    const heartIcon = r.user_liked ? 'fas' : 'far';
                    
                    html += `
                        <div class="comment" id="comment-${r.id}" style="margin-bottom:10px;">
                            <img src="${r.user_pic}" class="comment-avatar">
                            <div class="comment-content">
                                <div class="comment-header">
                                    <span class="comment-username">${r.username}</span>
                                    <span class="comment-time">${timeAgo}</span>
                                </div>
                                <div class="comment-text">${r.content}</div>
                                <div class="comment-actions">
                                    <span class="comment-action ${likedClass}" onclick="likeComment(${r.id}, this)">
                                        <i class="${heartIcon} fa-heart"></i> ${r.likes}
                                    </span>
                                    ${r.user_id === currentUser.id ? `
                                        <span class="comment-action" onclick="deleteComment(${r.id})">
                                            <i class="far fa-trash-alt"></i> Delete
                                        </span>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                document.getElementById(`replies-${commentId}`).innerHTML = html;
            } catch (error) {
                console.error('Error loading replies:', error);
            }
        }

        async function likeComment(commentId, element) {
            try {
                const res = await fetch(BASE_URL + `/api/comment/${commentId}/like`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await res.json();
                
                if (data.success) {
                    const heartIcon = element.querySelector('i');
                    if (data.liked) {
                        heartIcon.classList.remove('far');
                        heartIcon.classList.add('fas');
                        element.classList.add('liked');
                    } else {
                        heartIcon.classList.remove('fas');
                        heartIcon.classList.add('far');
                        element.classList.remove('liked');
                    }
                    element.innerHTML = `<i class="${heartIcon.className}"></i> ${data.likes}`;
                }
            } catch (error) {
                console.error('Error liking comment:', error);
            }
        }

        function showReplyInput(commentId) {
            document.getElementById(`reply-input-${commentId}`).style.display = 'flex';
        }

        async function addReply(parentId) {
            const input = document.getElementById(`reply-text-${parentId}`);
            const content = input.value.trim();
            if (!content) return;
            
            try {
                const res = await fetch(BASE_URL + '/api/comment', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        video_id: currentVideoId,
                        parent_id: parentId,
                        content: content
                    })
                });
                
                if (res.ok) {
                    input.value = '';
                    document.getElementById(`reply-input-${parentId}`).style.display = 'none';
                    loadReplies(parentId);
                }
            } catch (error) {
                console.error('Error adding reply:', error);
            }
        }

        async function deleteComment(commentId) {
            if (!confirm('Delete this comment?')) return;
            
            try {
                const res = await fetch(BASE_URL + `/api/comment/${commentId}/delete`, {
                    method: 'DELETE'
                });
                
                if (res.ok) {
                    document.getElementById(`comment-${commentId}`).remove();
                }
            } catch (error) {
                console.error('Error deleting comment:', error);
            }
        }

        function handleNewComment(data) {
            const commentsList = document.getElementById(`comments-list-${data.video_id}`);
            if (commentsList) {
                const commentHtml = renderComment(data.comment);
                commentsList.insertAdjacentHTML('afterbegin', commentHtml);
            }
        }

        function handleNewReply(data) {
            const repliesSection = document.getElementById(`replies-${data.parent_id}`);
            if (repliesSection) {
                const replyHtml = renderComment(data.comment);
                repliesSection.insertAdjacentHTML('beforeend', replyHtml);
            }
        }

        function getTimeAgo(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const seconds = Math.floor((now - date) / 1000);
            
            if (seconds < 60) return 'just now';
            const minutes = Math.floor(seconds / 60);
            if (minutes < 60) return `${minutes}m`;
            const hours = Math.floor(minutes / 60);
            if (hours < 24) return `${hours}h`;
            const days = Math.floor(hours / 24);
            if (days < 7) return `${days}d`;
            return date.toLocaleDateString();
        }

        function toggleComments(videoId) {
            const comments = document.getElementById(`comments-${videoId}`);
            if (comments) {
                comments.style.display = comments.style.display === 'none' ? 'block' : 'none';
            }
        }

        async function addComment(videoId) {
            const input = document.getElementById(`comment-input-${videoId}`);
            const content = input.value.trim();
            if (!content) return;
            
            try {
                const res = await fetch(BASE_URL + '/api/comment', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        video_id: videoId,
                        content: content
                    })
                });
                
                if (res.ok) {
                    input.value = '';
                    loadComments(videoId, `comments-list-${videoId}`);
                }
            } catch (error) {
                console.error('Error adding comment:', error);
            }
        }

        // ==================== FOLLOWERS/FOLLOWING MODAL FUNCTIONS ====================
        function openFollowersModal(userId) {
            currentProfileUserId = userId;
            document.getElementById('followersModal').classList.add('active');
            loadFollowers(userId);
        }

        function closeFollowersModal() {
            document.getElementById('followersModal').classList.remove('active');
        }

        function openFollowingModal(userId) {
            currentProfileUserId = userId;
            document.getElementById('followingModal').classList.add('active');
            loadFollowing(userId);
        }

        function closeFollowingModal() {
            document.getElementById('followingModal').classList.remove('active');
        }

        async function loadFollowers(userId) {
            try {
                const res = await fetch(BASE_URL + `/api/followers/${userId}`);
                followersData = await res.json();
                displayFollowers(followersData);
            } catch (error) {
                console.error('Error loading followers:', error);
            }
        }

        async function loadFollowing(userId) {
            try {
                const res = await fetch(BASE_URL + `/api/following/${userId}`);
                followingData = await res.json();
                displayFollowing(followingData);
            } catch (error) {
                console.error('Error loading following:', error);
            }
        }

        function displayFollowers(users) {
            let html = '';
            users.forEach(u => {
                const followBtnText = u.is_current_user ? 'You' : (u.is_following ? 'Following' : 'Follow');
                const followBtnClass = u.is_following ? 'following' : '';
                const disabled = u.is_current_user ? 'disabled' : '';
                
                html += `
                    <div class="user-list-item">
                        <img src="${u.profile_pic}" alt="${u.username}">
                        <div class="user-list-info">
                            <div class="user-list-username">${u.username}</div>
                            <div class="user-list-name">${u.full_name}</div>
                        </div>
                        <button class="user-list-follow-btn ${followBtnClass}" ${disabled} onclick="followFromModal(${u.id}, this)">
                            ${followBtnText}
                        </button>
                    </div>
                `;
            });
            
            if (users.length === 0) {
                html = '<p style="text-align: center; padding: 20px;">No followers yet</p>';
            }
            
            document.getElementById('followersList').innerHTML = html;
        }

        function displayFollowing(users) {
            let html = '';
            users.forEach(u => {
                const followBtnText = u.is_current_user ? 'You' : (u.is_following ? 'Following' : 'Follow');
                const followBtnClass = u.is_following ? 'following' : '';
                const disabled = u.is_current_user ? 'disabled' : '';
                
                html += `
                    <div class="user-list-item">
                        <img src="${u.profile_pic}" alt="${u.username}">
                        <div class="user-list-info">
                            <div class="user-list-username">${u.username}</div>
                            <div class="user-list-name">${u.full_name}</div>
                        </div>
                        <button class="user-list-follow-btn ${followBtnClass}" ${disabled} onclick="followFromModal(${u.id}, this)">
                            ${followBtnText}
                        </button>
                    </div>
                `;
            });
            
            if (users.length === 0) {
                html = '<p style="text-align: center; padding: 20px;">Not following anyone yet</p>';
            }
            
            document.getElementById('followingList').innerHTML = html;
        }

        function searchFollowers() {
            const searchTerm = document.getElementById('followersSearch').value.toLowerCase();
            const filtered = followersData.filter(u => 
                u.username.toLowerCase().includes(searchTerm) || 
                u.full_name.toLowerCase().includes(searchTerm)
            );
            displayFollowers(filtered);
        }

        function searchFollowing() {
            const searchTerm = document.getElementById('followingSearch').value.toLowerCase();
            const filtered = followingData.filter(u => 
                u.username.toLowerCase().includes(searchTerm) || 
                u.full_name.toLowerCase().includes(searchTerm)
            );
            displayFollowing(filtered);
        }

        async function followFromModal(userId, btn) {
            if (userId === currentUser.id) return;
            
            try {
                const res = await fetch(BASE_URL + `/api/follow/${userId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await res.json();
                
                if (data.following) {
                    btn.textContent = 'Following';
                    btn.classList.add('following');
                    
                    if (document.getElementById('followersModal').classList.contains('active')) {
                        await loadFollowers(currentProfileUserId);
                    }
                    if (document.getElementById('followingModal').classList.contains('active')) {
                        await loadFollowing(currentProfileUserId);
                    }
                } else {
                    btn.textContent = 'Follow';
                    btn.classList.remove('following');
                    
                    if (document.getElementById('followersModal').classList.contains('active')) {
                        await loadFollowers(currentProfileUserId);
                    }
                    if (document.getElementById('followingModal').classList.contains('active')) {
                        await loadFollowing(currentProfileUserId);
                    }
                }
            } catch (error) {
                console.error('Error following user:', error);
            }
        }

        // ==================== LOAD HOME WITH COMMENTS ====================
        async function loadHome() {
            try {
                const res = await fetch(BASE_URL + '/api/videos');
                const videos = await res.json();
                
                let html = '<div class="feed">';
                if (videos.length === 0) {
                    html += '<p style="text-align: center; padding: 50px;">No videos yet. Be the first to upload!</p>';
                } else {
                    videos.forEach(v => {
                        currentVideoId = v.id;
                        html += `
                            <div class="post" id="post-${v.id}">
                                <div class="post-header">
                                    <img src="${v.profile_pic}">
                                    <div><strong>${v.full_name}</strong></div>
                                </div>
                                <div class="video-container">
                                    <video src="${BASE_URL}${v.file_path}" controls playsinline></video>
                                </div>
                                <div class="post-actions">
                                    <i class="far fa-heart" onclick="likeVideo(${v.id}, this)"></i>
                                    <i class="far fa-comment" onclick="toggleComments(${v.id})"></i>
                                    <i class="far fa-paper-plane"></i>
                                    <i class="far fa-bookmark"></i>
                                </div>
                                <div class="post-likes">${v.likes} likes</div>
                                <div class="post-caption">
                                    <strong>${v.username}</strong> ${v.title}
                                </div>
                                <div class="comments-section" id="comments-${v.id}" style="display:none;">
                                    <div id="comments-list-${v.id}"></div>
                                    <div style="display:flex; gap:10px; margin-top:15px; padding:10px; border-top:1px solid #eee;">
                                        <input type="text" id="comment-input-${v.id}" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:20px;" placeholder="Add comment...">
                                        <button onclick="addComment(${v.id})" style="background:#667eea; color:white; border:none; padding:8px 20px; border-radius:20px; cursor:pointer;">Post</button>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                }
                html += '</div>';
                document.getElementById('main').innerHTML = html;
                
                videos.forEach(v => {
                    loadComments(v.id, `comments-list-${v.id}`);
                });
                
            } catch (error) {
                console.error('Error loading home:', error);
            }
        }

        async function loadReels() {
            try {
                const res = await fetch(BASE_URL + '/api/reels');
                const reels = await res.json();
                
                let html = '<div class="reels-grid">';
                if (reels.length === 0) {
                    html = '<p style="text-align: center; padding: 50px;">No reels yet. Create your first reel!</p>';
                } else {
                    reels.forEach(r => {
                        html += `
                            <div class="reel">
                                <div class="reel-media">
                                    <video src="${BASE_URL}${r.file_path}" loop muted playsinline></video>
                                </div>
                                <div style="padding: 10px;">
                                    <img src="${r.profile_pic}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover;"> ${r.full_name}<br>
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
                const res = await fetch(BASE_URL + '/api/chat/users');
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
                    fetch(BASE_URL + '/api/chat/users'),
                    fetch(BASE_URL + `/api/messages/${userId}`)
                ]);
                const users = await usersRes.json();
                const messages = await msgsRes.json();
                const chatUser = users.find(u => u.id === userId);
                currentChatUser = chatUser;
                
                let html = `
                    <div class="chat-container">
                        <div style="padding: 15px; border-bottom: 1px solid #eee;">
                            <i class="fas fa-arrow-left" onclick="loadChatList()" style="cursor: pointer;"></i>
                            <img src="${chatUser.pic}" style="width: 40px; height: 40px; border-radius: 50%; margin-left: 10px; object-fit: cover;">
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
                    fetch(BASE_URL + `/api/profile/${userId}`),
                    fetch(BASE_URL + `/api/user-videos/${userId}`)
                ]);
                const profile = await profileRes.json();
                const videos = await videosRes.json();
                
                let actionButton = '';
                if (userId === currentUser.id) {
                    actionButton = `<button class="edit-profile-btn" onclick="openEditProfileModal()">Edit Profile</button>`;
                } else {
                    const statusRes = await fetch(BASE_URL + `/api/follow/status/${userId}`);
                    const status = await statusRes.json();
                    actionButton = `<button class="follow-btn ${status.status === 'following' ? 'following' : ''}" onclick="toggleFollow(${userId})">
                        ${status.status === 'following' ? 'Following ✓' : 'Follow'}
                    </button>`;
                }
                
                let html = `
                    <div class="profile-header">
                        <div class="profile-info">
                            <img src="${profile.pic}" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover;">
                            <div>
                                <div style="display: flex; align-items: center; gap: 20px;">
                                    <h2>${profile.username}</h2>
                                    ${actionButton}
                                </div>
                                <div class="profile-stats">
                                    <div class="stat-item" onclick="openFollowersModal(${userId})">
                                        <div class="stat-number">${profile.followers}</div>
                                        <div class="stat-label">followers</div>
                                    </div>
                                    <div class="stat-item" onclick="openFollowingModal(${userId})">
                                        <div class="stat-number">${profile.following}</div>
                                        <div class="stat-label">following</div>
                                    </div>
                                    <div class="stat-item">
                                        <div class="stat-number">${profile.posts}</div>
                                        <div class="stat-label">posts</div>
                                    </div>
                                </div>
                                <div><strong>${profile.name}</strong></div>
                                <div style="white-space: pre-line;">${profile.bio || ''}</div>
                            </div>
                        </div>
                    </div>
                    <div class="profile-posts">
                `;
                
                videos.forEach(v => {
                    html += `<div class="profile-post">
                        <video src="${BASE_URL}${v.file_path}" style="width: 100%; height: 100%; object-fit: cover;"></video>
                    </div>`;
                });
                
                if (videos.length === 0) {
                    html += '<p style="text-align: center; padding: 50px; grid-column: 1/-1;">No posts yet</p>';
                }
                
                html += '</div>';
                document.getElementById('main').innerHTML = html;
            } catch (error) {
                console.error('Error loading profile:', error);
            }
        }

        async function toggleFollow(userId) {
            try {
                const res = await fetch(BASE_URL + `/api/follow/${userId}`, {method: 'POST'});
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
                    const res = await fetch(BASE_URL + `/upload/${type}`, {
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
