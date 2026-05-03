"""
routes/student.py — Student Routes
====================================
Routes: dashboard, profile, jobs, community, learning, insights, skill-map,
        assessments, resources, video recommendations, skill gap analysis,
        results/recommendations, award badge
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify
from bson.objectid import ObjectId
from core.utils import fetch_youtube_videos


def register_student(app, users_col, results_col, db, fs):
    """Register all student-facing routes on the Flask app."""

    # ── Student Dashboard ─────────────────────────────────────────────────────
    @app.route('/student/dashboard')
    def student_dashboard():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        uid     = ObjectId(session['user_id'])
        user    = users_col.find_one({'_id': uid})
        results = list(results_col.find({'user_id': uid}))
        recs    = [
            {
                'skill': r['skill'],
                'score': r['score'],
                'level': 'Beginner' if r['score'] < 60 else ('Intermediate' if r['score'] < 80 else 'Advanced'),
            }
            for r in results
        ]
        trending = list(results_col.aggregate([
            {'$group': {'_id': '$skill', 'attempts': {'$sum': 1}, 'avg_score': {'$avg': '$score'}}},
            {'$sort': {'attempts': -1}},
            {'$limit': 5},
        ]))
        posts = list(db['community_posts'].find().sort('_id', -1).limit(4))
        return render_template('student/student_dashboard.html',
                               user=user, results=results, recs=recs,
                               trending=trending, posts=posts)

    # ── Edit Profile ──────────────────────────────────────────────────────────
    @app.route('/edit_profile', methods=['GET', 'POST'])
    def edit_profile():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        user = users_col.find_one({'_id': ObjectId(session['user_id'])})
        if request.method == 'POST':
            upd = {
                'name':                     request.form.get('name', user.get('name')),
                'college':                  request.form.get('college', ''),
                'skills':                   request.form.get('skills', '').split(','),
                'bio':                      request.form.get('bio', ''),
                'linkedin':                 request.form.get('linkedin', ''),
                'google_drive_resume_link': request.form.get('google_drive_resume_link', ''),
            }
            users_col.update_one({'_id': ObjectId(session['user_id'])}, {'$set': upd})
            session['name'] = upd['name']
            flash('Profile updated!', 'success')
            return redirect(url_for('student_dashboard'))
        return render_template('student/edit_profile.html', user=user)

    # ── Jobs (Matched + All) ──────────────────────────────────────────────────
    @app.route('/jobs')
    def jobs():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        verified = [
            r['skill']
            for r in results_col.find({'user_id': ObjectId(session['user_id']), 'gap_identified': False})
        ]
        all_jobs      = list(db['jobs'].find().sort('_id', -1))
        matched_jobs  = []
        other_jobs    = []
        for job in all_jobs:
            job_skills = set(job.get('required_skills', []))
            if job_skills and any(v in job_skills for v in verified):
                job['is_match'] = True
                matched_jobs.append(job)
            else:
                job['is_match'] = False
                other_jobs.append(job)
        listings = matched_jobs + other_jobs
        return render_template('student/jobs.html', jobs=listings, skills=verified)

    # ── Video Recommendations ─────────────────────────────────────────────────
    @app.route('/video_recommendations')
    def video_recommendations():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        gaps       = list(results_col.find({'user_id': ObjectId(session['user_id']), 'gap_identified': True}))
        all_videos = {g['skill']: fetch_youtube_videos(g['skill']) for g in gaps}
        return render_template('student/video_recommendations.html', all_videos=all_videos)

    # ── Learning Hub ──────────────────────────────────────────────────────────
    @app.route('/learning_hub')
    def learning_hub():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
        recs    = [
            {
                'skill': r['skill'],
                'score': r['score'],
                'level': 'Beginner' if r['score'] < 60 else ('Intermediate' if r['score'] < 80 else 'Advanced'),
            }
            for r in results
        ]
        return render_template('student/learning_hub.html', recs=recs)

    # ── Insights Panel ────────────────────────────────────────────────────────
    @app.route('/insights_panel')
    def insights_panel():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        trending = list(results_col.aggregate([
            {'$group': {'_id': '$skill', 'attempts': {'$sum': 1}, 'avg_score': {'$avg': '$score'}}},
            {'$sort': {'attempts': -1}},
            {'$limit': 10},
        ]))
        return render_template('student/insights_panel.html', trending=trending)

    # ── Community ─────────────────────────────────────────────────────────────
    @app.route('/community')
    def community():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        posts = list(db['community_posts'].find().sort('_id', -1).limit(20))
        return render_template('student/community.html', posts=posts)

    @app.route('/community/post', methods=['POST'])
    def community_post():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        content = request.form.get('content', '').strip()
        if content:
            db['community_posts'].insert_one({
                'user_id': ObjectId(session['user_id']),
                'author':  session.get('name', 'Student'),
                'content': content,
            })
        return redirect(url_for('community'))

    @app.route('/community/comment/<post_id>', methods=['POST'])
    def community_comment(post_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        text = request.form.get('comment', '').strip()
        if text:
            comment = {
                'author': session.get('name', 'User'),
                'role':   session.get('role', 'student'),
                'text':   text,
            }
            db['community_posts'].update_one(
                {'_id': ObjectId(post_id)},
                {'$push': {'comments': comment}}
            )
        return redirect(url_for('community'))

    @app.route('/community/delete/<post_id>', methods=['POST'])
    def community_delete_post(post_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        post = db['community_posts'].find_one({'_id': ObjectId(post_id)})
        if post and (session.get('role') == 'admin' or str(post.get('user_id')) == session['user_id']):
            db['community_posts'].delete_one({'_id': ObjectId(post_id)})
            flash('Post removed.', 'success')
        return redirect(url_for('community'))

    # ── Skill Gap Analysis ────────────────────────────────────────────────────
    @app.route('/skill_gap_analysis')
    def skill_gap_analysis():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
        return render_template('student/skill_gap_analysis.html',
                               gaps=[r for r in results if r.get('gap_identified')],
                               mastered=[r for r in results if not r.get('gap_identified')])

    # ── Profile Management ────────────────────────────────────────────────────
    @app.route('/profile_management')
    def profile_management():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        user        = users_col.find_one({'_id': ObjectId(session['user_id'])})
        results     = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
        resume_file = None
        if user.get('uploaded_resume_id'):
            try:
                resume_file = fs.get(ObjectId(user['uploaded_resume_id']))
            except Exception:
                pass
        return render_template('student/profile_management.html',
                               user=user, results=results,
                               badges=user.get('badges', []),
                               resume_file=resume_file)

    # ── Award Badge (AJAX) ────────────────────────────────────────────────────
    @app.route('/award_badge', methods=['POST'])
    def award_badge():
        if 'user_id' not in session or session.get('role') != 'student':
            return jsonify({'error': 'Unauthorized'}), 401
        data  = request.json
        skill = data.get('skill')
        score = data.get('score', 0)
        if score >= 60:
            badge = {
                'skill': skill,
                'score': score,
                'level': 'Verified' if score >= 80 else 'Certified',
            }
            users_col.update_one(
                {'_id': ObjectId(session['user_id'])},
                {'$addToSet': {'badges': badge}}
            )
            return jsonify({'awarded': True, 'badge': badge})
        return jsonify({'awarded': False})

    # ── Student Profile Page ──────────────────────────────────────────────────
    @app.route('/student/profile')
    def student_profile():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        user        = users_col.find_one({'_id': ObjectId(session['user_id'])})
        results     = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
        resume_file = None
        if user.get('uploaded_resume_id'):
            try:
                resume_file = fs.get(ObjectId(user['uploaded_resume_id']))
            except Exception:
                pass
        return render_template('student/student_profile_page.html',
                               user=user, results=results, resume_file=resume_file)

    # ── Skill Map Visualization ───────────────────────────────────────────────
    @app.route('/student/skill-map')
    def skill_map():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
        return render_template('student/skill_map_visualization.html', results=results)

    # ── Deep Insights Analytics ───────────────────────────────────────────────
    @app.route('/student/insights')
    def deep_insights():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
        return render_template('student/deep_insights_analytics.html', results=results)

    # ── Test / Assessment Selection ───────────────────────────────────────────
    @app.route('/student/assessments')
    def test_selection():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
        return render_template('test/test_selection_1.html', results=results)

    # ── Curated Resources Library ─────────────────────────────────────────────
    @app.route('/student/resources')
    def curated_resources():
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('login'))
        return render_template('student/curated_resources_library.html')

    # ── Results & Recommendations ─────────────────────────────────────────────
    @app.route('/recommendations/<skill>')
    def results_recommendations(skill):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_result = results_col.find_one(
            {'user_id': ObjectId(session['user_id']), 'skill': skill},
            sort=[('_id', -1)],
        )
        videos = []
        if user_result and user_result.get('gap_identified'):
            videos = fetch_youtube_videos(skill)
        return render_template('student/results_recommendations.html',
                               skill=skill, result=user_result, videos=videos)
