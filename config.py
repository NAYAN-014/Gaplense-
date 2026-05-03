"""
config.py — GapLens Platform Configuration
==========================================
Saari settings aur environment variables yahan define hain.
Kuch bhi change karna ho (DB URI, secret key, admin email) — bas yahan aao.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Flask ─────────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'gaplens_dev_secret')

    # ── MongoDB ───────────────────────────────────────────────────────────────
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')

    # ── Google OAuth ──────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID     = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # ── Default Admin Credentials ─────────────────────────────────────────────
    DEFAULT_ADMIN_EMAIL    = 'gaplensvip@gmail.com'
    DEFAULT_ADMIN_PASSWORD = 'vip@123'

    # ── Resume Upload Settings ────────────────────────────────────────────────
    ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}
    MAX_RESUME_SIZE           = 5 * 1024 * 1024  # 5 MB
