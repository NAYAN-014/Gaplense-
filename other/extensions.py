"""
extensions.py — GapLens Shared Extensions
==========================================
MongoDB, GridFS, aur OAuth objects yahan initialize hote hain.
Circular imports se bachne ke liye sab kuch ek jagah rakha gaya hai.
"""

from pymongo import MongoClient
import gridfs
from authlib.integrations.flask_client import OAuth


def init_db(mongo_uri: str):
    """
    MongoDB client aur sabhi collections initialize karo.
    Returns: (db, users_col, results_col, questions_col, fs)
    """
    try:
        client        = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        print("[DB] MongoDB connected successfully!")
    except Exception as e:
        print(f"[DB WARNING] MongoDB connection failed: {e}")
        print("[DB WARNING] App will start but database features won't work.")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db            = client['gaplens']
    users_col     = db['users']
    results_col   = db['test_results']
    questions_col = db['questions']
    fs            = gridfs.GridFS(db)
    return db, users_col, results_col, questions_col, fs


def init_oauth(app):
    """
    Google OAuth initialize karo.
    Returns: (oauth, google)
    """
    oauth  = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile https://www.googleapis.com/auth/drive.file'
        },
    )
    return oauth, google


def seed_default_admin(users_col, config):
    """
    Default admin account ensure karo database mein.
    Agar exist nahi karta toh create karo, warna password sync karo.
    """
    admin_email    = config['DEFAULT_ADMIN_EMAIL']
    admin_password = config['DEFAULT_ADMIN_PASSWORD']

    if not users_col.find_one({'email': admin_email}):
        users_col.insert_one({
            'name':                   'GapLens Admin',
            'email':                  admin_email,
            'password':               admin_password,
            'role':                   'admin',
            'college':                '',
            'skills':                 [],
            'bio':                    'Platform Administrator',
            'linkedin':               '',
            'google_drive_resume_link': '',
        })
        print(f"[SEED] Default admin created: {admin_email}")
    else:
        users_col.update_one(
            {'email': admin_email},
            {'$set': {'password': admin_password, 'role': 'admin'}}
        )
