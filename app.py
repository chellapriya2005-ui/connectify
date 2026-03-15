# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Connectify</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
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
        
        /* Desktop Sidebar */
        .sidebar { width: 220px; height: 100vh; background: white; border-right: 1px solid #dbdbdb; position: fixed; left: 0; top: 0; padding: 20px; z-index: 100; }
        .sidebar .logo { font-size: 24px; font-weight: bold; margin-bottom: 30px; color: #667eea; }
        .sidebar ul { list-style: none; }
        .sidebar li { padding: 15px; margin: 5px 0; border-radius: 10px; cursor: pointer; display: flex; align-items: center; gap: 10px; }
        .sidebar li:hover { background: #f5f5f5; }
        .sidebar li.active { background: #f0f2f5; }
        .sidebar li.delete { color: #ff4444; }
        
        /* Top Header */
        .top-header {
            position: fixed;
            top: 0;
            left: 220px;
            right: 0;
            height: 60px;
            background: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 25px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 99;
        }

        .header-title {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }

        .profile-section {
            display: flex;
            align-items: center;
        }

        .profile-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            object-fit: cover;
            border: 2px solid #667eea;
        }
        
        /* Mobile Header */
        .mobile-header {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: white;
            border-bottom: 1px solid #dbdbdb;
            padding: 0 16px;
            align-items: center;
            justify-content: space-between;
            z-index: 100;
        }
        .mobile-header .logo {
            font-size: 20px;
            font-weight: bold;
            color: #667eea;
            cursor: pointer;
        }
        .mobile-header .profile-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            object-fit: cover;
            border: 2px solid #667eea;
        }
        
        /* Dropdown Menus */
        .dropdown-menu {
            display: none;
            position: fixed;
            top: 70px;
            right: 16px;
            width: 250px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            z-index: 1000;
            overflow: hidden;
        }
        .dropdown-menu.active {
            display: block;
        }
        .dropdown-item {
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.3s;
        }
        .dropdown-item:hover {
            background: #f5f5f5;
        }
        .dropdown-item i {
            width: 20px;
            color: #667eea;
        }
        .dropdown-item.delete-item {
            color: #ff4444;
        }
        .dropdown-item.delete-item i {
            color: #ff4444;
        }
        .dropdown-item.logout-item {
            color: #ed4956;
        }
        .dropdown-item.logout-item i {
            color: #ed4956;
        }
        
        /* Main Content */
        .main { 
            margin-left: 220px; 
            margin-top: 60px;
            padding: 20px; 
            min-height: calc(100vh - 60px);
            background: #fafafa;
        }
        
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
            max-height: 600px;
            overflow: hidden;
        }
        .video-container video { 
            width: 100%;
            height: auto;
            max-height: 600px;
            object-fit: contain;
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
        
        /* Reels Grid */
        .reels-grid { 
            display: grid; 
            grid-template-columns: repeat(3, 1fr); 
            gap: 20px; 
            max-width: 1200px;
            margin: 0 auto;
        }
        .reel { 
            background: white; 
            border-radius: 12px; 
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .reel:hover {
            transform: scale(1.02);
        }
        .reel-media { 
            aspect-ratio: 9/16; 
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }
        .reel-media video { 
            width: 100%;
            height: 100%;
            object-fit: cover;
            background: black;
        }
        
        /* Stories Section - ALWAYS VISIBLE */
        .stories-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            overflow-x: auto;
            white-space: nowrap;
        }
        .stories-wrapper {
            display: inline-flex;
            gap: 20px;
        }
        .story-item {
            display: inline-block;
            text-align: center;
            cursor: pointer;
            width: 80px;
        }
        .story-avatar {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            padding: 3px;
            background: linear-gradient(45deg, #f09433, #d62976, #962fbf, #4f5bd5);
            margin-bottom: 5px;
        }
        .story-avatar img {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid white;
        }
        .story-username {
            font-size: 12px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .my-story {
            position: relative;
        }
        .my-story .plus-icon {
            position: absolute;
            bottom: 25px;
            right: 5px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            border: 2px solid white;
        }

        /* Story Viewer */
        .story-viewer {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: black;
            z-index: 3000;
            display: none;
            flex-direction: column;
        }
        .story-viewer.active {
            display: flex;
        }
        .story-header {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            padding: 20px;
            background: linear-gradient(to bottom, rgba(0,0,0,0.5), transparent);
            color: white;
            z-index: 10;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .story-header img {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid white;
        }
        .story-progress {
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            display: flex;
            gap: 5px;
            z-index: 20;
        }
        .progress-bar {
            height: 3px;
            background: rgba(255,255,255,0.3);
            flex: 1;
            border-radius: 3px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            width: 0%;
            background: white;
            transition: width 5s linear;
        }
        .story-media {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
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
            z-index: 30;
            width: 40px;
            height: 40px;
            background: rgba(0,0,0,0.5);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .story-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 40px;
            cursor: pointer;
            padding: 20px;
            z-index: 30;
        }
        .story-prev { left: 10px; }
        .story-next { right: 10px; }
        
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
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: background 0.3s;
        }
        .edit-profile-btn:hover {
            background: #1877f2;
        }
        .edit-profile-btn i {
            font-size: 14px;
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
            z-index: 2000;
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
        
        .create-modal { 
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            background: rgba(0,0,0,0.8); 
            display: none; 
            justify-content: center; 
            align-items: center; 
            z-index: 2000; 
        }
        .create-modal-content { 
            background: white; 
            border-radius: 20px; 
            width: 400px; 
            padding: 20px; 
        }
        .create-option {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 10px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .create-option:hover {
            background: #f5f5f5;
        }
        .create-option i {
            margin-right: 10px;
            color: #667eea;
        }
        
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
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .top-header { display: none; }
            .mobile-header { display: flex; }
            .main { 
                margin-left: 0; 
                margin-top: 60px;
                padding: 16px;
            }
            .profile-info { flex-direction: column; gap: 20px; }
            .profile-stats { gap: 20px; }
            .reels-grid { grid-template-columns: repeat(2,1fr); gap: 10px; }
            .story-nav {
                font-size: 30px;
                padding: 10px;
            }
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
        <!-- Desktop Sidebar -->
        <div class="sidebar">
            <div class="logo">Connectify</div>
            <ul>
                <li onclick="showPage('home')" class="active" id="menu-home"><i class="fas fa-home"></i> Home</li>
                <li onclick="showPage('reels')" id="menu-reels"><i class="fas fa-film"></i> Reels</li>
                <li onclick="showPage('stories')" id="menu-stories"><i class="fas fa-clock"></i> Stories</li>
                <li onclick="showPage('chat')" id="menu-chat"><i class="fas fa-paper-plane"></i> Messages</li>
                <li onclick="showPage('profile')" id="menu-profile"><i class="fas fa-user"></i> Profile</li>
                <li onclick="openCreateModal()"><i class="fas fa-plus-circle"></i> Create</li>
                <li onclick="showDeleteConfirm()" style="color: #ff4444;"><i class="fas fa-trash-alt"></i> Delete Account</li>
                <li onclick="logout()" style="color: #ed4956;"><i class="fas fa-sign-out-alt"></i> Logout</li>
            </ul>
        </div>

        <!-- Top Header - Desktop -->
        <header class="top-header">
            <div class="header-title">Connectify</div>
            <div class="profile-section">
                <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" class="profile-icon" id="desktopProfileIcon" onclick="toggleDropdown('desktop')" alt="Profile">
            </div>
        </header>

        <!-- Desktop Dropdown Menu -->
        <div class="dropdown-menu" id="desktopDropdown">
            <div class="dropdown-item" onclick="showPage('home'); closeDropdown('desktop')">
                <i class="fas fa-home"></i> Home
            </div>
            <div class="dropdown-item" onclick="showPage('reels'); closeDropdown('desktop')">
                <i class="fas fa-film"></i> Reels
            </div>
            <div class="dropdown-item" onclick="showPage('stories'); closeDropdown('desktop')">
                <i class="fas fa-clock"></i> Stories
            </div>
            <div class="dropdown-item" onclick="showPage('chat'); closeDropdown('desktop')">
                <i class="fas fa-paper-plane"></i> Messages
            </div>
            <div class="dropdown-item" onclick="showPage('profile'); closeDropdown('desktop')">
                <i class="fas fa-user"></i> Profile
            </div>
            <div class="dropdown-item" onclick="openCreateModal(); closeDropdown('desktop')">
                <i class="fas fa-plus-circle"></i> Create
            </div>
            <div class="dropdown-item delete-item" onclick="showDeleteConfirm(); closeDropdown('desktop')">
                <i class="fas fa-trash-alt"></i> Delete Account
            </div>
            <div class="dropdown-item logout-item" onclick="logout(); closeDropdown('desktop')">
                <i class="fas fa-sign-out-alt"></i> Logout
            </div>
        </div>

        <!-- Mobile Header with Profile Icon -->
        <div class="mobile-header">
            <div class="logo" onclick="showPage('home')">Connectify</div>
            <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" id="mobileProfileIcon" class="profile-icon" onclick="toggleDropdown('mobile')" alt="Profile">
        </div>

        <!-- Mobile Dropdown Menu -->
        <div class="dropdown-menu" id="mobileDropdown">
            <div class="dropdown-item" onclick="showPage('home'); closeDropdown('mobile')">
                <i class="fas fa-home"></i> Home
            </div>
            <div class="dropdown-item" onclick="showPage('reels'); closeDropdown('mobile')">
                <i class="fas fa-film"></i> Reels
            </div>
            <div class="dropdown-item" onclick="showPage('stories'); closeDropdown('mobile')">
                <i class="fas fa-clock"></i> Stories
            </div>
            <div class="dropdown-item" onclick="showPage('chat'); closeDropdown('mobile')">
                <i class="fas fa-paper-plane"></i> Messages
            </div>
            <div class="dropdown-item" onclick="showPage('profile'); closeDropdown('mobile')">
                <i class="fas fa-user"></i> Profile
            </div>
            <div class="dropdown-item" onclick="openCreateModal(); closeDropdown('mobile')">
                <i class="fas fa-plus-circle"></i> Create
            </div>
            <div class="dropdown-item delete-item" onclick="showDeleteConfirm(); closeDropdown('mobile')">
                <i class="fas fa-trash-alt"></i> Delete Account
            </div>
            <div class="dropdown-item logout-item" onclick="logout(); closeDropdown('mobile')">
                <i class="fas fa-sign-out-alt"></i> Logout
            </div>
        </div>

        <!-- Main Content Area -->
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
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">Username</label>
                        <input type="text" id="editUsername" name="username" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;" required>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">Full Name</label>
                        <input type="text" id="editFullName" name="full_name" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 5px;">Bio</label>
                        <textarea id="editBio" name="bio" rows="4" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; resize: none;" maxlength="150" oninput="updateBioCount()"></textarea>
                        <div style="text-align: right; font-size: 12px; color: #999;">
                            <span id="bioCount">0</span>/150
                        </div>
                    </div>
                    
                    <div style="text-align: right; margin-bottom: 15px;">
                        <a href="#" onclick="openPasswordModal(); return false;" style="color: #667eea; text-decoration: none; font-size: 14px;">
                            <i class="fas fa-key"></i> Change Password
                        </a>
                    </div>
                    
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
            <button onclick="closeCreateModal()" style="margin-top: 20px; width: 100%; padding: 10px; background: #f0f0f0; border: none; border-radius: 10px; cursor: pointer;">Close</button>
        </div>
    </div>

    <!-- Story Viewer Modal -->
    <div class="story-viewer" id="storyViewer">
        <div class="story-progress" id="storyProgress"></div>
        <div class="story-header" id="storyHeader"></div>
        <div class="story-close" onclick="closeStoryViewer()">&times;</div>
        <div class="story-nav story-prev" onclick="navigateStory('prev')">&#10094;</div>
        <div class="story-nav story-next" onclick="navigateStory('next')">&#10095;</div>
        <div class="story-media" id="storyMedia"></div>
    </div>

    <input type="file" id="fileInput" style="display: none;" accept="video/*,image/*">

    <script>
        let currentUser = null;
        let socket = null;
        let currentChatUser = null;
        let currentVideoId = null;
        let currentProfileUserId = null;
        let followersData = [];
        let followingData = [];
        let currentStories = [];
        let currentStoryIndex = 0;
        let storyTimer = null;
        
        const BASE_URL = window.location.origin;

        // ==================== HELPER FUNCTIONS ====================
        function toggleDropdown(type) {
            document.getElementById(type + 'Dropdown').classList.toggle('active');
        }

        function closeDropdown(type) {
            document.getElementById(type + 'Dropdown').classList.remove('active');
        }

        function updateProfileIcons() {
            if (currentUser && currentUser.pic) {
                document.getElementById('desktopProfileIcon').src = currentUser.pic;
                document.getElementById('mobileProfileIcon').src = currentUser.pic;
            }
        }

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

        // ==================== AUTH FUNCTIONS ====================
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
                    updateProfileIcons();
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
                    updateProfileIcons();
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
            socket.on('new_story', () => {
                if (document.getElementById('menu-stories').classList.contains('active')) {
                    loadStories();
                }
            });
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
            else if (page === 'stories') loadStories();
            else if (page === 'chat') loadChatList();
            else if (page === 'profile') loadProfile(currentUser.id);
            
            closeDropdown('mobile');
            closeDropdown('desktop');
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
                    updateProfileIcons();
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

        // ==================== UPLOAD FUNCTIONS ====================
        function uploadVideo() {
            closeCreateModal();
            const input = document.getElementById('fileInput');
            input.accept = 'video/*';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const title = prompt('Enter title for your video:');
                if (!title) return;
                
                const formData = new FormData();
                formData.append('video', file);
                formData.append('title', title);
                
                try {
                    const res = await fetch(BASE_URL + '/upload/video', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (res.ok) {
                        alert('Video uploaded successfully!');
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

        function uploadReel() {
            closeCreateModal();
            const input = document.getElementById('fileInput');
            input.accept = 'video/*';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const title = prompt('Enter title for your reel:');
                if (!title) return;
                
                const music = prompt('Enter music name:', 'Original Audio');
                
                const formData = new FormData();
                formData.append('reel', file);
                formData.append('title', title);
                formData.append('music', music || 'Original Audio');
                
                try {
                    const res = await fetch(BASE_URL + '/upload/reel', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (res.ok) {
                        alert('Reel uploaded successfully!');
                        showPage('reels');
                    } else {
                        alert('Upload failed');
                    }
                } catch (error) {
                    alert('Error uploading reel');
                }
            };
            input.click();
        }

        function uploadStory() {
            closeCreateModal();
            const input = document.getElementById('fileInput');
            input.accept = 'image/*,video/*';
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
                    
                    if (res.ok) {
                        alert('Story uploaded successfully!');
                        if (document.getElementById('menu-stories').classList.contains('active')) {
                            loadStories();
                        }
                    } else {
                        alert('Upload failed');
                    }
                } catch (error) {
                    alert('Error uploading story');
                }
            };
            input.click();
        }

        // ==================== LOAD HOME ====================
        async function loadHome() {
            try {
                // Load videos
                const videosRes = await fetch(BASE_URL + '/api/videos');
                const videos = await videosRes.json();
                
                // Load stories for the stories bar
                const storiesRes = await fetch(BASE_URL + '/api/stories');
                let stories = [];
                try {
                    stories = await storiesRes.json();
                } catch (e) {
                    stories = [];
                }
                
                let html = '<div class="feed">';
                
                // ALWAYS show stories section with "Your Story"
                html += '<div class="stories-container"><div class="stories-wrapper">';
                
                // Add "Your Story" option - ALWAYS VISIBLE
                html += `
                    <div class="story-item my-story" onclick="uploadStory()">
                        <div class="story-avatar" style="position: relative;">
                            <img src="${currentUser.pic}">
                            <span class="plus-icon"><i class="fas fa-plus"></i></span>
                        </div>
                        <div class="story-username">Your Story</div>
                    </div>
                `;
                
                // Add other users' stories if they exist
                if (stories && stories.length > 0) {
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
                }
                
                html += '</div></div>';
                
                // Add videos
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
                                    <video src="${BASE_URL}${v.file_path}" controls playsinline preload="metadata"></video>
                                </div>
                                <div class="post-actions">
                                    <i class="${v.user_liked ? 'fas' : 'far'} fa-heart" onclick="likeVideo(${v.id}, this)"></i>
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
                
                // Load comments for each video
                videos.forEach(v => {
                    loadComments(v.id, `comments-list-${v.id}`);
                });
                
            } catch (error) {
                console.error('Error loading home:', error);
                document.getElementById('main').innerHTML = '<p style="text-align: center; padding: 50px;">Error loading content.</p>';
            }
        }

        // ==================== LOAD REELS ====================
        async function loadReels() {
            try {
                const res = await fetch(BASE_URL + '/api/reels');
                const reels = await res.json();
                
                let html = '<div class="reels-grid">';
                if (!reels || reels.length === 0) {
                    html = '<p style="text-align: center; padding: 50px;">No reels yet. Create your first reel!</p>';
                } else {
                    reels.forEach(r => {
                        html += `
                            <div class="reel">
                                <div class="reel-media">
                                    <video src="${BASE_URL}${r.file_path}" loop muted playsinline preload="metadata"></video>
                                </div>
                                <div style="padding: 10px;">
                                    <img src="${r.profile_pic}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover; margin-right: 5px;"> 
                                    <strong>${r.full_name}</strong><br>
                                    <small>❤️ ${r.likes} • 🎵 ${r.music || 'Original Audio'}</small>
                                </div>
                            </div>
                        `;
                    });
                }
                html += '</div>';
                document.getElementById('main').innerHTML = html;
                
                // Add click to play/pause
                document.querySelectorAll('.reel-media video').forEach(video => {
                    video.addEventListener('click', function() {
                        if (this.paused) {
                            this.play();
                        } else {
                            this.pause();
                        }
                    });
                });
            } catch (error) {
                console.error('Error loading reels:', error);
                document.getElementById('main').innerHTML = '<p style="text-align: center; padding: 50px;">Error loading reels.</p>';
            }
        }

        // ==================== STORY FUNCTIONS ====================
        async function loadStories() {
            try {
                const res = await fetch(BASE_URL + '/api/stories/all');
                const stories = await res.json();
                
                let html = '<div class="feed">';
                
                if (!stories || stories.length === 0) {
                    html += '<p style="text-align: center; padding: 50px;">No stories available. Upload a story to get started!</p>';
                } else {
                    // Group stories by user
                    const userStories = {};
                    stories.forEach(story => {
                        if (!userStories[story.user_id]) {
                            userStories[story.user_id] = {
                                user_id: story.user_id,
                                username: story.username,
                                user_pic: story.user_pic,
                                stories: []
                            };
                        }
                        userStories[story.user_id].stories.push(story);
                    });
                    
                    html += '<div class="stories-container"><div class="stories-wrapper">';
                    
                    // Add "Your Story" option
                    html += `
                        <div class="story-item my-story" onclick="uploadStory()">
                            <div class="story-avatar" style="position: relative;">
                                <img src="${currentUser.pic}">
                                <span class="plus-icon"><i class="fas fa-plus"></i></span>
                            </div>
                            <div class="story-username">Your Story</div>
                        </div>
                    `;
                    
                    Object.values(userStories).forEach(user => {
                        if (user.user_id !== currentUser.id) {
                            html += `
                                <div class="story-item" onclick="viewStories(${user.user_id})">
                                    <div class="story-avatar">
                                        <img src="${user.user_pic}">
                                    </div>
                                    <div class="story-username">${user.username}</div>
                                </div>
                            `;
                        }
                    });
                    
                    html += '</div></div>';
                    
                    // Display recent stories
                    html += '<h3 style="margin: 20px 0;">Recent Stories</h3>';
                    stories.slice(0, 10).forEach(story => {
                        const isVideo = story.media_type === 'video';
                        html += `
                            <div class="post" onclick="viewStories(${story.user_id})" style="cursor: pointer;">
                                <div class="post-header">
                                    <img src="${story.user_pic}">
                                    <div>
                                        <strong>${story.username}</strong>
                                        <div style="font-size: 12px; color: #999;">${getTimeAgo(story.created_at)}</div>
                                    </div>
                                </div>
                                <div class="video-container" style="max-height: 300px;">
                                    ${isVideo ? 
                                        `<video src="${BASE_URL}${story.file_path}" controls playsinline></video>` : 
                                        `<img src="${BASE_URL}${story.file_path}" style="max-width: 100%; max-height: 300px; object-fit: contain;">`
                                    }
                                </div>
                            </div>
                        `;
                    });
                }
                
                html += '</div>';
                document.getElementById('main').innerHTML = html;
                
            } catch (error) {
                console.error('Error loading stories:', error);
                document.getElementById('main').innerHTML = '<p style="text-align: center; padding: 50px;">Error loading stories.</p>';
            }
        }

        async function viewStories(userId) {
            try {
                const res = await fetch(BASE_URL + `/api/stories/user/${userId}`);
                const stories = await res.json();
                
                if (!stories || stories.length === 0) {
                    alert('No stories available');
                    return;
                }
                
                currentStories = stories;
                currentStoryIndex = 0;
                showStory(0);
                
            } catch (error) {
                console.error('Error loading user stories:', error);
                alert('Error loading stories');
            }
        }

        function showStory(index) {
            if (!currentStories || index < 0 || index >= currentStories.length) {
                closeStoryViewer();
                return;
            }
            
            currentStoryIndex = index;
            const story = currentStories[index];
            
            if (storyTimer) {
                clearTimeout(storyTimer);
            }
            
            let progressHTML = '';
            currentStories.forEach((s, i) => {
                progressHTML += `
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-${i}" style="width: ${i < index ? '100%' : (i === index ? '0%' : '0%')};"></div>
                    </div>
                `;
            });
            document.getElementById('storyProgress').innerHTML = progressHTML;
            
            document.getElementById('storyHeader').innerHTML = `
                <img src="${story.user_pic}">
                <div>
                    <strong>${story.username}</strong>
                    <div style="font-size: 12px;">${getTimeAgo(story.created_at)}</div>
                </div>
            `;
            
            const isVideo = story.media_type === 'video';
            document.getElementById('storyMedia').innerHTML = isVideo ?
                `<video src="${BASE_URL}${story.file_path}" autoplay playsinline></video>` :
                `<img src="${BASE_URL}${story.file_path}" style="max-width: 100%; max-height: 100%; object-fit: contain;">`;
            
            document.getElementById('storyViewer').classList.add('active');
            
            const progressFill = document.getElementById(`progress-${index}`);
            if (progressFill) {
                progressFill.style.width = '100%';
            }
            
            const duration = isVideo ? 15000 : 5000;
            storyTimer = setTimeout(() => {
                navigateStory('next');
            }, duration);
        }

        function navigateStory(direction) {
            if (direction === 'next') {
                if (currentStoryIndex < currentStories.length - 1) {
                    showStory(currentStoryIndex + 1);
                } else {
                    closeStoryViewer();
                }
            } else if (direction === 'prev') {
                if (currentStoryIndex > 0) {
                    showStory(currentStoryIndex - 1);
                }
            }
        }

        function closeStoryViewer() {
            document.getElementById('storyViewer').classList.remove('active');
            if (storyTimer) {
                clearTimeout(storyTimer);
            }
            const video = document.querySelector('#storyMedia video');
            if (video) {
                video.pause();
            }
        }

        // ==================== CHAT FUNCTIONS ====================
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
                                    <small>${u.last_msg || 'No messages yet'}</small>
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
                        <div style="padding: 15px; border-bottom: 1px solid #eee; display: flex; align-items: center;">
                            <i class="fas fa-arrow-left" onclick="loadChatList()" style="cursor: pointer; margin-right: 15px;"></i>
                            <img src="${chatUser.pic}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; object-fit: cover;">
                            <div>
                                <strong>${chatUser.name}</strong><br>
                                <small style="color: #999;">${chatUser.online ? '● Online' : 'Offline'}</small>
                            </div>
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

        // ==================== LOAD PROFILE ====================
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
                    actionButton = `<button class="edit-profile-btn" onclick="openEditProfileModal()">
                        <i class="fas fa-user-edit"></i> Edit Profile
                    </button>`;
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
                                <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
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
                        <video src="${BASE_URL}${v.file_path}" style="width: 100%; height: 100%; object-fit: cover;" preload="metadata"></video>
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

        // Close dropdowns when clicking outside
        document.addEventListener('click', function(event) {
            const mobileDropdown = document.getElementById('mobileDropdown');
            const desktopDropdown = document.getElementById('desktopDropdown');
            const mobileIcon = document.getElementById('mobileProfileIcon');
            const desktopIcon = document.getElementById('desktopProfileIcon');
            
            if (mobileDropdown && mobileIcon) {
                if (!mobileDropdown.contains(event.target) && !mobileIcon.contains(event.target)) {
                    mobileDropdown.classList.remove('active');
                }
            }
            
            if (desktopDropdown && desktopIcon) {
                if (!desktopDropdown.contains(event.target) && !desktopIcon.contains(event.target)) {
                    desktopDropdown.classList.remove('active');
                }
            }
        });

        // Close modals when clicking outside
        window.onclick = function(event) {
            const modals = ['createModal', 'followersModal', 'followingModal', 'editProfileModal', 'passwordModal'];
            modals.forEach(modalId => {
                const modal = document.getElementById(modalId);
                if (event.target === modal) {
                    modal.classList.remove('active');
                    modal.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
'''
