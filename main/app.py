"""
main/app.py — GapLens Flask Application Factory
=================================================
Yahan Flask app banta hai. Routes register hote hain.
Run karne ke liye project root se: python run.py
"""

import os
import sys

# ── Project root path (main/ ka parent) ──────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Python path mein project root add karo (routes/, core/, other/ sab milenge)
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, '.env'))

from flask import Flask
from other.config     import Config
from other.extensions import init_db, init_oauth, seed_default_admin

# ── Routes (har role ka alag file) ───────────────────────────────────────────
from routes.auth       import register_auth
from routes.student    import register_student
from routes.recruiter  import register_recruiter
from routes.admin      import register_admin
from routes.diagnostic import register_diagnostic
from routes.resume     import register_resume

# ── Flask App — template & static folders explicitly set to project root ─────
app = Flask(
    __name__,
    template_folder=os.path.join(ROOT, 'templates'),
    static_folder=os.path.join(ROOT, 'static'),
)
app.config.from_object(Config)

# ── Initialize Database & OAuth ───────────────────────────────────────────────
db, users_col, results_col, questions_col, fs = init_db(app.config['MONGO_URI'])
oauth, google = init_oauth(app)

# ── Seed Default Admin ────────────────────────────────────────────────────────
try:
    seed_default_admin(users_col, app.config)
except Exception as e:
    print(f"[SEED WARNING] Could not seed admin: {e}")

# ── Register All Routes ───────────────────────────────────────────────────────
register_auth(app, users_col, google)
register_student(app, users_col, results_col, db, fs)
register_recruiter(app, users_col, results_col, db)
register_admin(app, users_col, results_col, questions_col, db)
register_diagnostic(app, users_col, results_col, questions_col, db)
register_resume(app, users_col, results_col, fs)
