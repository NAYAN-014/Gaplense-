"""
app.py — GapLens Platform Entry Point
=======================================
Sirf app create karta hai, config load karta hai, aur sab routes register karta hai.
Kisi bhi route ke liye → routes/ folder dekho.
Kisi bhi setting ke liye → config.py dekho.
"""

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import Config
from extensions import init_db, init_oauth, seed_default_admin

# ── Routes (har role ka alag file) ───────────────────────────────────────────
from routes.auth       import register_auth
from routes.student    import register_student
from routes.recruiter  import register_recruiter
from routes.admin      import register_admin
from routes.diagnostic import register_diagnostic
from routes.resume     import register_resume


# ── App Factory ───────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

# ── Initialize Database & OAuth ───────────────────────────────────────────────
db, users_col, results_col, questions_col, fs = init_db(app.config['MONGO_URI'])
oauth, google = init_oauth(app)

# ── Seed Default Admin ────────────────────────────────────────────────────────
seed_default_admin(users_col, app.config)

# ── Register All Routes ───────────────────────────────────────────────────────
register_auth(app, users_col, google)
register_student(app, users_col, results_col, db, fs)
register_recruiter(app, users_col, results_col, db)
register_admin(app, users_col, results_col, questions_col, db)
register_diagnostic(app, users_col, results_col, questions_col, db)
register_resume(app, users_col, results_col, fs)


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)
