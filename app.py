# ==================== COMPLETE WORKING REELS SECTION ====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Connectify - Reels</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        
        body {
            background: black;
            overflow-x: hidden;
        }
        
        /* Auth Page */
        .auth-page {
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
        }
        
        .auth-card {
            background: white;
            padding: 40px 30px;
            width: 400px;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .auth-card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 32px;
            text-align: center;
        }
        
        .tab-container {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        
        .auth-tab {
            flex: 1;
            text-align: center;
            padding: 10px;
            cursor: pointer;
            color: #999;
            background: none;
            border: none;
            font-size: 16px;
        }
        
        .auth-tab.active {
            color: #667eea;
            border-bottom: 2px solid #667eea;
        }
        
        .auth-form {
            display: none;
        }
        
        .auth-form.active {
            display: block;
        }
        
        .auth-form input, .auth-form textarea {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 10px;
        }
        
        .auth-btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 16px;
            cursor: pointer;
            font-weight: 600;
        }
        
        /* App Container */
        .app {
            display: none;
            background: black;
            min-height: 100vh;
        }
        
        /* Mobile Bottom Navigation */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.95);
            backdrop-filter: blur(20px);
            display: flex;
            justify-content: space-around;
            padding: 12px 0;
            z-index: 100;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            color: #8e8e8e;
            transition: color 0.2s;
        }
        
        .nav-item i {
            font-size: 24px;
        }
        
        .nav-item span {
            font-size: 10px;
        }
        
        .nav-item.active {
            color: white;
        }
        
        /* Main Content Area */
        .main-content {
            padding-bottom: 70px;
            background: black;
            min-height: 100vh;
        }
        
        /* Reels Grid - Instagram Style */
        .reels-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 20px;
            padding: 0 10px;
        }
        
        .reel {
            background: #1a1a1a;
            border-radius: 12px;
            overflow: hidden;
            cursor: pointer;
            border: 1px solid #262626;
            position: relative;
        }
        
        .reel-media {
            position: relative;
            width: 100%;
            aspect-ratio: 9/16;
            background: black;
        }
        
        .reel-media video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .duration {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .reel-info {
            padding: 10px;
            color: white;
        }
        
        .reel-info small {
            color: #8e8e8e;
        }
        
        .reel .delete-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255,0,0,0.8);
            color: white;
            border: none;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 10;
            transition: 0.2s;
        }
        
        .reel .delete-btn:hover {
            background: red;
            transform: scale(1.1);
        }
        
        /* Fullscreen Reels Player */
        .reels-player {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: black;
            z-index: 2000;
            display: none;
        }
        
        .reels-player.active {
            display: block;
        }
        
        .reels-container {
            height: 100%;
            overflow-y: scroll;
            scroll-snap-type: y mandatory;
            -webkit-overflow-scrolling: touch;
        }
        
        .reel-slide {
            height: 100vh;
            width: 100%;
            scroll-snap-align: start;
            position: relative;
            background: black;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .reel-slide video {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        
        /* Reel Overlay */
        .reel-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
            padding: 80px 16px 20px;
            color: white;
        }
        
        .reel-user {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }
        
        .reel-user img {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid white;
        }
        
        .reel-username {
            font-weight: 600;
            font-size: 15px;
        }
        
        .reel-caption {
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .reel-music {
            font-size: 12px;
            color: #ccc;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        /* Right Side Actions */
        .reel-actions {
            position: absolute;
            right: 12px;
            bottom: 100px;
            display: flex;
            flex-direction: column;
            gap: 24px;
            z-index: 10;
        }
        
        .reel-action {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            cursor: pointer;
        }
        
        .reel-action i {
            font-size: 28px;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }
        
        .reel-action span {
            font-size: 11px;
            color: white;
        }
        
        .reel-action i.fa-heart.fas {
            color: #ed4956;
        }
        
        /* Header */
        .reels-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            padding: 16px;
            background: linear-gradient(to bottom, rgba(0,0,0,0.5), transparent);
            z-index: 20;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }
        
        .close-reels {
            background: rgba(0,0,0,0.5);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 20px;
        }
        
        .reels-title {
            font-weight: 600;
            font-size: 16px;
        }
        
        /* Home Feed */
        .feed {
            max-width: 600px;
            margin: 0 auto;
            background: black;
        }
        
        .post {
            background: black;
            margin-bottom: 20px;
            border-bottom: 1px solid #262626;
        }
        
        .post-header {
            padding: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .post-header img {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
        }
        
        .post-header strong {
            color: white;
        }
        
        .video-container {
            width: 100%;
            background: black;
        }
        
        .video-container video {
            width: 100%;
            max-height: 600px;
            object-fit: contain;
        }
        
        .post-actions {
            padding: 12px;
            display: flex;
            gap: 20px;
        }
        
        .post-actions i {
            font-size: 26px;
            cursor: pointer;
            color: white;
        }
        
        .post-actions i.fa-heart.fas {
            color: #ed4956;
        }
        
        .post-likes {
            padding: 0 12px 8px;
            font-weight: bold;
            color: white;
        }
        
        .post-caption {
            padding: 0 12px 12px;
            color: white;
        }
        
        /* Stories */
        .stories-container {
            background: black;
            padding: 12px;
            overflow-x: auto;
            white-space: nowrap;
            border-bottom: 1px solid #262626;
        }
        
        .stories-wrapper {
            display: inline-flex;
            gap: 16px;
        }
        
        .story-item {
            display: inline-block;
            text-align: center;
            cursor: pointer;
            width: 70px;
        }
        
        .story-avatar {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            padding: 2px;
            background: linear-gradient(45deg, #f09433, #d62976, #962fbf, #4f5bd5);
            margin-bottom: 5px;
        }
        
        .story-avatar img {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid black;
        }
        
        .story-username {
            font-size: 11px;
            color: white;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .my-story {
            position: relative;
        }
        
        .plus-icon {
            position: absolute;
            bottom: 20px;
            right: 5px;
            background: #0095f6;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            border: 2px solid black;
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 3000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: black;
            width: 90%;
            max-width: 400px;
            border-radius: 12px;
            overflow: hidden;
        }
        
        .modal-header {
            padding: 16px;
            border-bottom: 1px solid #262626;
            display: flex;
            justify-content: space-between;
            color: white;
        }
        
        .modal-body {
            padding: 16px;
            max-height: 70vh;
            overflow-y: auto;
        }
        
        .create-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 3000;
        }
        
        .create-modal-content {
            background: black;
            border-radius: 12px;
            width: 90%;
            max-width: 350px;
            padding: 20px;
            color: white;
        }
        
        .create-option {
            padding: 15px;
            border: 1px solid #262626;
            border-radius: 10px;
            margin-bottom: 10px;
            cursor: pointer;
            text-align: center;
        }
        
        .create-option:hover {
            background: #1a1a1a;
        }
        
        /* Profile */
        .profile-header {
            padding: 20px;
            color: white;
        }
        
        .profile-info {
            display: flex;
            gap: 30px;
            align-items: center;
        }
        
        .profile-info img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
        }
        
        .profile-stats {
            display: flex;
            gap: 30px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
            cursor: pointer;
        }
        
        .stat-number {
            font-size: 18px;
            font-weight: bold;
        }
        
        .stat-label {
            font-size: 12px;
            color: #8e8e8e;
        }
        
        .follow-btn {
            background: #0095f6;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 8px;
            cursor: pointer;
        }
        
        .profile-posts {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 3px;
        }
        
        .profile-post {
            aspect-ratio: 1;
            background: #1a1a1a;
        }
        
        .profile-post video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        /* Chat */
        .chat-container {
            background: black;
            height: calc(100vh - 70px);
            display: flex;
            flex-direction: column;
            color: white;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .message {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 18px;
            margin: 5px 0;
        }
        
        .message.sent {
            align-self: flex-end;
            background: #0095f6;
            color: white;
            margin-left: auto;
        }
        
        .message.received {
            align-self: flex-start;
            background: #262626;
            color: white;
        }
        
        .chat-input {
            display: flex;
            padding: 15px;
            gap: 10px;
            border-top: 1px solid #262626;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 25px;
            background: #262626;
            color: white;
        }
        
        .chat-input button {
            background: #0095f6;
            color: white;
            border: none;
            width: 45px;
            height: 45px;
            border-radius: 50%;
            cursor: pointer;
        }
        
        .chat-list {
            color: white;
        }
        
        .chat-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            border-bottom: 1px solid #262626;
            cursor: pointer;
        }
        
        .chat-item img {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
        }
        
        /* Story Viewer */
        .story-viewer {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: black;
            z-index: 4000;
            display: none;
        }
        
        .story-viewer.active {
            display: block;
        }
        
        .story-media {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .story-media video, .story-media img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .story-close {
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            font-size: 30px;
            cursor: pointer;
            z-index: 10;
        }
        
        /* Hide scrollbar */
        .reels-container::-webkit-scrollbar {
            display: none;
        }
        
        .reels-container {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
    </style>
</head>
<body>
    <!-- Auth Page -->
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
                <input type="text" id="reg-username" placeholder="Username">
                <input type="password" id="reg-password" placeholder="Password">
                <input type="text" id="reg-fullname" placeholder="Full Name">
                <textarea id="reg-bio" placeholder="Bio"></textarea>
                <button class="auth-btn" onclick="register()">Create Account</button>
            </div>
        </div>
    </div>
    
    <!-- Main App -->
    <div class="app" id="app">
        <!-- Bottom Navigation -->
        <div class="bottom-nav">
            <div class="nav-item active" onclick="showPage('home')" id="nav-home">
                <i class="fas fa-home"></i>
                <span>Home</span>
            </div>
            <div class="nav-item" onclick="showPage('reels')" id="nav-reels">
                <i class="fas fa-film"></i>
                <span>Reels</span>
            </div>
            <div class="nav-item" onclick="showPage('stories')" id="nav-stories">
                <i class="fas fa-clock"></i>
                <span>Stories</span>
            </div>
            <div class="nav-item" onclick="showPage('chat')" id="nav-chat">
                <i class="fas fa-comment"></i>
                <span>Messages</span>
            </div>
            <div class="nav-item" onclick="showPage('profile')" id="nav-profile">
                <i class="fas fa-user"></i>
                <span>Profile</span>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content" id="mainContent"></div>
    </div>
    
    <!-- Reels Player -->
    <div class="reels-player" id="reelsPlayer">
        <div class="reels-header">
            <div class="close-reels" onclick="closeReelsPlayer()">✕</div>
            <div class="reels-title">Reels</div>
            <div style="width: 36px;"></div>
        </div>
        <div class="reels-container" id="reelsContainer"></div>
    </div>
    
    <!-- Create Modal -->
    <div class="create-modal" id="createModal">
        <div class="create-modal-content">
            <h3 style="margin-bottom: 20px; text-align: center;">Create New</h3>
            <div class="create-option" onclick="uploadVideo()">
                <i class="fas fa-video"></i> Upload Video Post
            </div>
            <div class="create-option" onclick="uploadReel()">
                <i class="fas fa-film"></i> Upload Reel
            </div>
            <div class="create-option" onclick="uploadStory()">
                <i class="fas fa-clock"></i> Add Story
            </div>
            <button onclick="closeCreateModal()" style="margin-top: 20px; width: 100%; padding: 10px; background: #262626; border: none; border-radius: 10px; color: white; cursor: pointer;">Close</button>
        </div>
    </div>
    
    <!-- Story Viewer -->
    <div class="story-viewer" id="storyViewer">
        <div class="story-close" onclick="closeStoryViewer()">✕</div>
        <div class="story-media" id="storyMedia"></div>
    </div>
    
    <!-- Modals -->
    <div class="modal" id="followersModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Followers</h3>
                <span onclick="closeFollowersModal()" style="cursor: pointer;">✕</span>
            </div>
            <div class="modal-body" id="followersList"></div>
        </div>
    </div>
    
    <div class="modal" id="followingModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Following</h3>
                <span onclick="closeFollowingModal()" style="cursor: pointer;">✕</span>
            </div>
            <div class="modal-body" id="followingList"></div>
        </div>
    </div>
    
    <div class="modal" id="editProfileModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Edit Profile</h3>
                <span onclick="closeEditProfileModal()" style="cursor: pointer;">✕</span>
            </div>
            <div class="modal-body">
                <input type="text" id="editUsername" placeholder="Username" style="width: 100%; padding: 10px; margin-bottom: 10px; background: #262626; border: none; border-radius: 8px; color: white;">
                <input type="text" id="editFullname" placeholder="Full Name" style="width: 100%; padding: 10px; margin-bottom: 10px; background: #262626; border: none; border-radius: 8px; color: white;">
                <textarea id="editBio" placeholder="Bio" rows="3" style="width: 100%; padding: 10px; margin-bottom: 10px; background: #262626; border: none; border-radius: 8px; color: white;"></textarea>
                <button onclick="updateProfile()" style="width: 100%; padding: 12px; background: #0095f6; border: none; border-radius: 8px; color: white; font-weight: bold;">Save</button>
            </div>
        </div>
    </div>
    
    <input type="file" id="fileInput" style="display: none;" accept="video/*">
    
    <script>
        let currentUser = null;
        let socket = null;
        let allReels = [];
        let currentReelIndex = 0;
        let currentStories = [];
        let isScrolling = false;
        
        const BASE_URL = window.location.origin;
        
        // ==================== AUTH FUNCTIONS ====================
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
                alert('Error: ' + error);
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
                    alert('Login failed');
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        function connectSocket() {
            socket = io(BASE_URL);
            socket.emit('join', {user_id: currentUser.id});
            
            // Listen for new reels
            socket.on('new_reel', () => {
                if (document.querySelector('.reels-grid')) {
                    loadReels();
                }
            });
            
            // Listen for video deletion
            socket.on('video_deleted', (data) => {
                if (document.querySelector('.reels-grid')) {
                    loadReels();
                }
            });
        }
        
        async function logout() {
            await fetch(BASE_URL + '/logout');
            if (socket) socket.disconnect();
            document.getElementById('app').style.display = 'none';
            document.getElementById('auth').style.display = 'flex';
        }
        
        // ==================== PAGE NAVIGATION ====================
        function showPage(page) {
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            document.getElementById(`nav-${page}`).classList.add('active');
            
            if (page === 'home') loadHome();
            else if (page === 'reels') loadReels();
            else if (page === 'stories') loadStories();
            else if (page === 'chat') loadChatList();
            else if (page === 'profile') loadProfile(currentUser.id);
        }
        
        // ==================== LOAD REELS - INSTAGRAM STYLE ====================
        async function loadReels() {
            try {
                const res = await fetch(BASE_URL + '/api/reels');
                const reels = await res.json();
                allReels = reels;
                
                let html = '<h3 style="color: white; margin-bottom: 20px; padding: 0 10px;">Reels</h3><div class="reels-grid">';
                
                if (!reels || reels.length === 0) {
                    html = '<div style="text-align: center; padding: 50px; color: white;">No reels yet. Create your first reel!</div>';
                } else {
                    reels.forEach((reel) => {
                        const isOwner = currentUser && reel.user_id === currentUser.id;
                        html += `<div class="reel" id="reel-${reel.id}" style="position:relative;">`;
                        
                        // Add delete button if this is the current user's reel
                        if (isOwner) {
                            html += `<button class="delete-btn" onclick="event.stopPropagation(); deleteReel(${reel.id})">
                                <i class="fas fa-trash"></i>
                            </button>`;
                        }
                        
                        html += `<div class="reel-media" onclick="viewReel('${BASE_URL}${reel.file_path}')">
                                <video src="${BASE_URL}${reel.file_path}" muted loop></video>
                                <span class="duration">15s</span>
                            </div>
                            <div class="reel-info">
                                <div style="display:flex; align-items:center; gap:5px; margin-bottom:5px;">
                                    <img src="${reel.profile_pic}" style="width:25px; height:25px; border-radius:50%;">
                                    <span>${reel.full_name}</span>
                                </div>
                                <div style="display:flex; justify-content:space-between;">
                                    <span>❤️ ${reel.likes || 0}</span>
                                    <span>👁️ ${reel.views || 0}</span>
                                </div>
                                <small>🎵 ${reel.music || 'Original Audio'}</small>
                            </div>
                        </div>`;
                    });
                }
                
                html += '</div>';
                document.getElementById('mainContent').innerHTML = html;
                
                // Add hover play effect for reels grid
                document.querySelectorAll('.reel-media video').forEach(video => {
                    video.addEventListener('mouseenter', () => {
                        video.play().catch(e => console.log('Hover play error:', e));
                    });
                    video.addEventListener('mouseleave', () => {
                        video.pause();
                        video.currentTime = 0;
                    });
                });
            } catch (error) {
                console.error('Error loading reels:', error);
                document.getElementById('mainContent').innerHTML = '<div style="text-align: center; padding: 50px; color: white;">Error loading reels</div>';
            }
        }
        
        // ==================== DELETE REEL ====================
        async function deleteReel(reelId) {
            if (!confirm('Are you sure you want to delete this reel?')) return;
            
            try {
                const res = await fetch(BASE_URL + '/delete/reel/' + reelId, {
                    method: 'DELETE'
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('Reel deleted successfully!');
                    loadReels(); // Refresh the reels grid
                } else {
                    alert('Failed to delete reel');
                }
            } catch (error) {
                console.error('Error deleting reel:', error);
                alert('Error deleting reel');
            }
        }
        
        // ==================== VIEW REEL (Fullscreen) ====================
        function viewReel(path) {
            const viewer = document.createElement('div');
            viewer.style.position = 'fixed';
            viewer.style.top = '0';
            viewer.style.left = '0';
            viewer.style.width = '100%';
            viewer.style.height = '100%';
            viewer.style.backgroundColor = 'black';
            viewer.style.zIndex = '5000';
            viewer.style.display = 'flex';
            viewer.style.alignItems = 'center';
            viewer.style.justifyContent = 'center';
            viewer.innerHTML = `
                <video src="${path}" controls autoplay style="max-width: 100%; max-height: 100%;"></video>
                <button onclick="this.parentElement.remove()" style="position: absolute; top: 20px; right: 20px; background: rgba(0,0,0,0.5); color: white; border: none; border-radius: 50%; width: 40px; height: 40px; font-size: 20px; cursor: pointer;">✕</button>
            `;
            document.body.appendChild(viewer);
        }
        
        // ==================== OPEN REELS PLAYER (Keep for compatibility) ====================
        function openReelsPlayer(startIndex) {
            // This is kept for compatibility but not used in new design
            viewReel(allReels[startIndex]?.file_path);
        }
        
        function closeReelsPlayer() {
            // This is kept for compatibility
            const container = document.getElementById('reelsContainer');
            if (container) {
                const videos = container.querySelectorAll('video');
                videos.forEach(video => {
                    video.pause();
                });
            }
            document.getElementById('reelsPlayer').classList.remove('active');
        }
        
        function shareReel(url) {
            if (navigator.share) {
                navigator.share({ title: 'Check out this reel!', url: url });
            } else {
                prompt('Copy this link:', url);
            }
        }
        
        function viewProfile(userId) {
            closeReelsPlayer();
            showPage('profile');
            loadProfile(userId);
        }
        
        // ==================== LOAD HOME ====================
        async function loadHome() {
            try {
                const videosRes = await fetch(BASE_URL + '/api/videos');
                const videos = await videosRes.json();
                
                let stories = [];
                try {
                    const storiesRes = await fetch(BASE_URL + '/api/stories');
                    stories = await storiesRes.json();
                } catch(e) {}
                
                let html = '<div class="feed">';
                
                // Stories
                html += '<div class="stories-container"><div class="stories-wrapper">';
                html += `
                    <div class="story-item my-story" onclick="uploadStory()">
                        <div class="story-avatar">
                            <img src="${currentUser.pic}">
                            <div class="plus-icon"><i class="fas fa-plus"></i></div>
                        </div>
                        <div class="story-username">Your Story</div>
                    </div>
                `;
                
                const uniqueUsers = {};
                stories.forEach(story => {
                    if (!uniqueUsers[story.user_id] && story.user_id !== currentUser.id) {
                        uniqueUsers[story.user_id] = story;
                        html += `
                            <div class="story-item" onclick="viewStories(${story.user_id})">
                                <div class="story-avatar">
                                    <img src="${story.user_pic}">
                                </div>
                                <div class="story-username">${story.username}</div>
                            </div>
                        `;
                    }
                });
                html += '</div></div>';
                
                // Videos
                videos.forEach(v => {
                    html += `
                        <div class="post">
                            <div class="post-header">
                                <img src="${v.profile_pic}">
                                <strong>${v.full_name}</strong>
                            </div>
                            <div class="video-container">
                                <video src="${BASE_URL}${v.file_path}" controls playsinline></video>
                            </div>
                            <div class="post-actions">
                                <i class="${v.user_liked ? 'fas' : 'far'} fa-heart" onclick="likeVideo(${v.id}, this)"></i>
                                <i class="far fa-comment"></i>
                                <i class="far fa-paper-plane"></i>
                            </div>
                            <div class="post-likes">${v.likes} likes</div>
                            <div class="post-caption"><strong>${v.username}</strong> ${v.title}</div>
                        </div>
                    `;
                });
                
                html += '</div>';
                document.getElementById('mainContent').innerHTML = html;
            } catch (error) {
                console.error('Error loading home:', error);
            }
        }
        
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
                    const likeSpan = element.closest('.post').querySelector('.post-likes');
                    if (likeSpan) likeSpan.innerText = data.likes + ' likes';
                }
            } catch (error) {
                console.error('Error liking video:', error);
            }
        }
        
        // ==================== STORIES ====================
        async function loadStories() {
            try {
                const res = await fetch(BASE_URL + '/api/stories/all');
                const stories = await res.json();
                
                let html = '<div class="feed"><div class="stories-container"><div class="stories-wrapper">';
                html += `
                    <div class="story-item my-story" onclick="uploadStory()">
                        <div class="story-avatar">
                            <img src="${currentUser.pic}">
                            <div class="plus-icon"><i class="fas fa-plus"></i></div>
                        </div>
                        <div class="story-username">Your Story</div>
                    </div>
                `;
                
                const uniqueUsers = {};
                stories.forEach(story => {
                    if (!uniqueUsers[story.user_id] && story.user_id !== currentUser.id) {
                        uniqueUsers[story.user_id] = story;
                        html += `
                            <div class="story-item" onclick="viewStories(${story.user_id})">
                                <div class="story-avatar">
                                    <img src="${story.user_pic}">
                                </div>
                                <div class="story-username">${story.username}</div>
                            </div>
                        `;
                    }
                });
                html += '</div></div>';
                
                stories.slice(0, 10).forEach(story => {
                    const isVideo = story.media_type === 'video';
                    html += `
                        <div class="post" onclick="viewStories(${story.user_id})">
                            <div class="post-header">
                                <img src="${story.user_pic}">
                                <strong>${story.username}</strong>
                            </div>
                            <div class="video-container">
                                ${isVideo ? 
                                    `<video src="${BASE_URL}${story.file_path}" controls></video>` : 
                                    `<img src="${BASE_URL}${story.file_path}" style="width: 100%;">`
                                }
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                document.getElementById('mainContent').innerHTML = html;
            } catch (error) {
                console.error('Error loading stories:', error);
            }
        }
        
        async function viewStories(userId) {
            try {
                const res = await fetch(BASE_URL + `/api/stories/user/${userId}`);
                const stories = await res.json();
                currentStories = stories;
                
                if (stories.length > 0) {
                    showStory(0);
                }
            } catch (error) {
                console.error('Error loading stories:', error);
            }
        }
        
        function showStory(index) {
            if (index >= currentStories.length) {
                closeStoryViewer();
                return;
            }
            
            const story = currentStories[index];
            const isVideo = story.media_type === 'video';
            
            document.getElementById('storyMedia').innerHTML = isVideo ?
                `<video src="${BASE_URL}${story.file_path}" autoplay playsinline></video>` :
                `<img src="${BASE_URL}${story.file_path}">`;
            
            document.getElementById('storyViewer').classList.add('active');
            
            // Auto-advance after 5 seconds
            setTimeout(() => {
                showStory(index + 1);
            }, 5000);
        }
        
        function closeStoryViewer() {
            document.getElementById('storyViewer').classList.remove('active');
            const video = document.querySelector('#storyMedia video');
            if (video) video.pause();
        }
        
        // ==================== CHAT ====================
        async function loadChatList() {
            try {
                const res = await fetch(BASE_URL + '/api/chat/users');
                const users = await res.json();
                
                let html = '<div class="chat-list">';
                users.forEach(u => {
                    html += `
                        <div class="chat-item" onclick="openChat(${u.id})">
                            <img src="${u.pic}">
                            <div>
                                <strong>${u.name}</strong>
                                <div style="font-size: 12px; color: #8e8e8e;">${u.last_msg || 'No messages'}</div>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                document.getElementById('mainContent').innerHTML = html;
            } catch (error) {
                console.error('Error loading chat:', error);
            }
        }
        
        async function openChat(userId) {
            try {
                const msgsRes = await fetch(BASE_URL + `/api/messages/${userId}`);
                const messages = await msgsRes.json();
                
                let html = `
                    <div class="chat-container">
                        <div style="padding: 15px; border-bottom: 1px solid #262626; display: flex; align-items: center;">
                            <i class="fas fa-arrow-left" onclick="loadChatList()" style="cursor: pointer; margin-right: 15px;"></i>
                            <span>Chat</span>
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
                
                document.getElementById('mainContent').innerHTML = html;
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
            const chat = document.getElementById('chatMessages');
            if (chat && msg.sender_id !== currentUser.id) {
                chat.innerHTML += `<div class="message received">${msg.content}</div>`;
                chat.scrollTop = chat.scrollHeight;
            }
        }
        
        // ==================== PROFILE ====================
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
                    actionButton = `<button class="follow-btn" onclick="openEditProfileModal()">Edit Profile</button>`;
                } else {
                    const statusRes = await fetch(BASE_URL + `/api/follow/status/${userId}`);
                    const status = await statusRes.json();
                    actionButton = `<button class="follow-btn" onclick="toggleFollow(${userId})">${status.status === 'following' ? 'Following' : 'Follow'}</button>`;
                }
                
                let html = `
                    <div class="profile-header">
                        <div class="profile-info">
                            <img src="${profile.pic}">
                            <div>
                                <h2>${profile.username}</h2>
                                ${actionButton}
                            </div>
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
                        <div>${profile.bio || ''}</div>
                    </div>
                    <div class="profile-posts">
                `;
                
                videos.forEach(v => {
                    html += `<div class="profile-post"><video src="${BASE_URL}${v.file_path}" preload="metadata"></video></div>`;
                });
                
                if (videos.length === 0) {
                    html += '<div style="text-align: center; padding: 50px; grid-column: 1/-1;">No posts yet</div>';
                }
                
                html += '</div>';
                document.getElementById('mainContent').innerHTML = html;
            } catch (error) {
                console.error('Error loading profile:', error);
            }
        }
        
        async function toggleFollow(userId) {
            try {
                await fetch(BASE_URL + `/api/follow/${userId}`, {method: 'POST'});
                loadProfile(userId);
            } catch (error) {
                console.error('Error toggling follow:', error);
            }
        }
        
        async function openFollowersModal(userId) {
            const res = await fetch(BASE_URL + `/api/followers/${userId}`);
            const users = await res.json();
            let html = '';
            users.forEach(u => {
                html += `<div style="display: flex; align-items: center; gap: 12px; padding: 10px; border-bottom: 1px solid #262626;">
                    <img src="${u.profile_pic}" style="width: 40px; height: 40px; border-radius: 50%;">
                    <div><strong>${u.username}</strong><br><small>${u.full_name}</small></div>
                </div>`;
            });
            document.getElementById('followersList').innerHTML = html;
            document.getElementById('followersModal').classList.add('active');
        }
        
        function closeFollowersModal() {
            document.getElementById('followersModal').classList.remove('active');
        }
        
        function openFollowingModal(userId) {
            document.getElementById('followingModal').classList.add('active');
        }
        
        function closeFollowingModal() {
            document.getElementById('followingModal').classList.remove('active');
        }
        
        function openEditProfileModal() {
            document.getElementById('editUsername').value = currentUser.username;
            document.getElementById('editFullname').value = currentUser.name || '';
            document.getElementById('editBio').value = currentUser.bio || '';
            document.getElementById('editProfileModal').classList.add('active');
        }
        
        function closeEditProfileModal() {
            document.getElementById('editProfileModal').classList.remove('active');
        }
        
        async function updateProfile() {
            const data = {
                username: document.getElementById('editUsername').value,
                full_name: document.getElementById('editFullname').value,
                bio: document.getElementById('editBio').value
            };
            
            try {
                const res = await fetch(BASE_URL + '/api/update-profile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                if (result.success) {
                    currentUser = result.user;
                    closeEditProfileModal();
                    loadProfile(currentUser.id);
                    alert('Profile updated!');
                }
            } catch (error) {
                console.error('Error updating profile:', error);
            }
        }
        
        // ==================== UPLOAD FUNCTIONS ====================
        function uploadVideo() {
            closeCreateModal();
            const input = document.getElementById('fileInput');
            input.accept = 'video/*';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const title = prompt('Enter title:');
                if (!title) return;
                
                const formData = new FormData();
                formData.append('video', file);
                formData.append('title', title);
                
                try {
                    const res = await fetch(BASE_URL + '/upload/video', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (data.success) {
                        alert('Video uploaded!');
                        showPage('home');
                    } else {
                        alert('Upload failed');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            };
            input.click();
        }
        
        function uploadReel() {
            closeCreateModal();
            const input = document.getElementById('fileInput');
            input.accept = 'video/*';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const title = prompt('Enter reel title:');
                if (!title) return;
                
                const music = prompt('Music name:', 'Original Audio');
                
                const formData = new FormData();
                formData.append('reel', file);
                formData.append('title', title);
                formData.append('music', music || 'Original Audio');
                
                try {
                    const res = await fetch(BASE_URL + '/upload/reel', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (data.success) {
                        alert('Reel uploaded!');
                        showPage('reels');
                    } else {
                        alert('Upload failed');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            };
            input.click();
        }
        
        function uploadStory() {
            closeCreateModal();
            const input = document.getElementById('fileInput');
            input.accept = 'video/*,image/*';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const formData = new FormData();
                formData.append('story', file);
                
                try {
                    const res = await fetch(BASE_URL + '/upload/story', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (data.success) {
                        alert('Story uploaded!');
                        showPage('home');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            };
            input.click();
        }
        
        function openCreateModal() {
            document.getElementById('createModal').style.display = 'flex';
        }
        
        function closeCreateModal() {
            document.getElementById('createModal').style.display = 'none';
        }
        
        // Socket events
        if (socket) {
            socket.on('new_message', handleNewMessage);
        }
    </script>
</body>
</html>
'''
