"""
routes/resume.py — Resume Upload / Download / Delete Routes
=============================================================
Routes: /generate-resume, /upload-resume, /download-resume, /delete-resume
"""

from flask import request, redirect, url_for, session, flash, send_file
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO
from utils import generate_and_email_pdf

ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_RESUME_SIZE           = 5 * 1024 * 1024  # 5 MB


def _allowed_resume_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS


def register_resume(app, users_col, results_col, fs):
    """Register all resume-related routes on the Flask app."""

    # ── Generate & Email PDF Resume ───────────────────────────────────────────
    @app.route('/generate-resume', methods=['POST'])
    def generate_resume():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('profile_management'))
        user            = users_col.find_one({'_id': ObjectId(session['user_id'])})
        raw             = results_col.find({'user_id': ObjectId(session['user_id'])})
        verified_skills = {r['skill']: round(r['score']) for r in raw}
        user_data       = {'name': user.get('name', 'Student'), 'verified_skills': verified_skills}
        success         = generate_and_email_pdf(user_data, user.get('email'))
        if success:
            flash('Resume generated and emailed to you!', 'success')
        else:
            flash('Resume generation failed. Please try again.', 'error')
        return redirect(url_for('profile_management'))

    # ── Upload Resume (GridFS) ────────────────────────────────────────────────
    @app.route('/upload-resume', methods=['POST'])
    def upload_resume():
        """Student uploads a resume file (PDF/DOC/DOCX) stored in GridFS."""
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))

        if 'resume_file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(url_for('student_profile'))

        file = request.files['resume_file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('student_profile'))

        if not _allowed_resume_file(file.filename):
            flash('Only PDF, DOC, or DOCX files are allowed.', 'error')
            return redirect(url_for('student_profile'))

        file_data = file.read()
        if len(file_data) > MAX_RESUME_SIZE:
            flash('File size exceeds 5 MB limit.', 'error')
            return redirect(url_for('student_profile'))

        # Delete old resume from GridFS if exists
        user   = users_col.find_one({'_id': ObjectId(session['user_id'])})
        old_id = user.get('uploaded_resume_id')
        if old_id:
            try:
                fs.delete(ObjectId(old_id))
            except Exception:
                pass

        filename = secure_filename(file.filename)
        file_id  = fs.put(
            file_data,
            filename=filename,
            content_type=file.content_type or 'application/octet-stream',
            upload_date=datetime.utcnow(),
            user_id=ObjectId(session['user_id']),
        )
        users_col.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {
                'uploaded_resume_id':       file_id,
                'uploaded_resume_filename': filename,
                'uploaded_resume_date':     datetime.utcnow(),
            }}
        )
        flash(f'Resume "{filename}" uploaded successfully!', 'success')
        return redirect(url_for('student_profile'))

    # ── Download Resume (GridFS) ──────────────────────────────────────────────
    @app.route('/download-resume')
    def download_resume():
        """Serve the student's uploaded resume file from GridFS."""
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        user    = users_col.find_one({'_id': ObjectId(session['user_id'])})
        file_id = user.get('uploaded_resume_id')
        if not file_id:
            flash('No resume uploaded yet.', 'error')
            return redirect(url_for('student_profile'))
        try:
            grid_file = fs.get(ObjectId(file_id))
            return send_file(
                BytesIO(grid_file.read()),
                mimetype=grid_file.content_type or 'application/octet-stream',
                as_attachment=True,
                download_name=grid_file.filename,
            )
        except Exception:
            flash('Could not download resume.', 'error')
            return redirect(url_for('student_profile'))

    # ── Delete Resume (GridFS) ────────────────────────────────────────────────
    @app.route('/delete-resume', methods=['POST'])
    def delete_resume():
        """Remove the uploaded resume from GridFS and user record."""
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        user    = users_col.find_one({'_id': ObjectId(session['user_id'])})
        file_id = user.get('uploaded_resume_id')
        if file_id:
            try:
                fs.delete(ObjectId(file_id))
            except Exception:
                pass
        users_col.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$unset': {
                'uploaded_resume_id':       '',
                'uploaded_resume_filename': '',
                'uploaded_resume_date':     '',
            }}
        )
        flash('Resume removed.', 'success')
        return redirect(url_for('student_profile'))
