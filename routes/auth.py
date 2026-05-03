"""
routes/auth.py — Authentication Routes
=======================================
Routes: /, /login, /signup, /logout, /auth/google, /auth/google/callback
"""

from flask import render_template, request, redirect, url_for, session, flash


def register_auth(app, users_col, google):
    """Register all authentication routes on the Flask app."""

    # ── Index / Root ──────────────────────────────────────────────────────────
    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('role')
            if role == 'student':
                return redirect(url_for('student_dashboard'))
            elif role == 'recruiter':
                return redirect(url_for('recruiter_dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin_dashboard'))
        return redirect(url_for('login'))

    # ── Login ─────────────────────────────────────────────────────────────────
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            identifier = request.form.get('username', '').strip()
            password   = request.form.get('password', '')
            user = users_col.find_one({
                '$or': [{'email': identifier}, {'username': identifier}]
            })
            if user and user.get('password') == password:
                session['user_id'] = str(user['_id'])
                session['role']    = user.get('role', 'student')
                session['name']    = user.get('name', 'User')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials. Please check your email/username and password.', 'error')
        return render_template('auth/login_page.html')

    # ── Signup ────────────────────────────────────────────────────────────────
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name     = request.form.get('name')
            email    = request.form.get('email')
            password = request.form.get('password')
            role     = request.form.get('role', 'student')

            if users_col.find_one({'email': email}):
                flash('Account already exists with this email.', 'error')
                return redirect(url_for('signup'))

            users_col.insert_one({
                'name':     name,
                'email':    email,
                'password': password,
                'role':     role,
            })
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        return render_template('auth/signup.html')

    # ── Logout ────────────────────────────────────────────────────────────────
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    # ── Google OAuth — Initiate ───────────────────────────────────────────────
    @app.route('/auth/google')
    def google_login():
        """Redirect user to Google's OAuth consent screen."""
        redirect_uri = url_for('google_callback', _external=True)
        return google.authorize_redirect(redirect_uri)

    # ── Google OAuth — Callback ───────────────────────────────────────────────
    @app.route('/auth/google/callback')
    def google_callback():
        """Handle the Google OAuth callback — create/update user in DB."""
        token     = google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            flash('Google login failed. Please try again.', 'error')
            return redirect(url_for('login'))

        email = user_info['email']
        name  = user_info.get('name', email)

        existing = users_col.find_one({'email': email})
        if not existing:
            result = users_col.insert_one({
                'name':      name,
                'email':     email,
                'password':  None,       # Google users have no local password
                'role':      'student',  # Default role; admin can change later
                'google_id': user_info['sub'],
                'avatar':    user_info.get('picture', ''),
            })
            user_id = str(result.inserted_id)
            role    = 'student'
        else:
            user_id = str(existing['_id'])
            role    = existing.get('role', 'student')
            users_col.update_one({'_id': existing['_id']}, {'$set': {
                'name':   name,
                'avatar': user_info.get('picture', ''),
            }})

        session['user_id']      = user_id
        session['role']         = role
        session['name']         = name
        session['google_token'] = token.get('access_token')

        return redirect(url_for('index'))
