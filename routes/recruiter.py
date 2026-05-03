"""
routes/recruiter.py — Recruiter Routes
========================================
Routes: /recruiter/dashboard, /recruiter/talent-search,
        /recruiter/post-job, /recruiter/my-jobs, /recruiter/delete-job/<job_id>
"""

from flask import render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId


def register_recruiter(app, users_col, results_col, db):
    """Register all recruiter-facing routes on the Flask app."""

    @app.route('/recruiter/dashboard')
    def recruiter_dashboard():
        if 'user_id' not in session or session.get('role') != 'recruiter':
            return redirect(url_for('login'))
        total_candidates = users_col.count_documents({'role': 'student'})
        total_verified   = results_col.count_documents({'gap_identified': False})
        avg_res          = list(results_col.aggregate([{'$group': {'_id': None, 'avg': {'$avg': '$score'}}}]))
        avg_score        = round(avg_res[0]['avg']) if avg_res else 0
        my_jobs_count    = db['jobs'].count_documents({'posted_by': ObjectId(session['user_id'])})
        top_results = list(results_col.aggregate([
            {'$sort': {'score': -1}}, {'$limit': 10},
            {'$lookup': {'from': 'users', 'localField': 'user_id', 'foreignField': '_id', 'as': 'user_info'}},
            {'$unwind': {'path': '$user_info', 'preserveNullAndEmptyArrays': True}},
        ]))
        top_candidates = [{
            'name':  r.get('user_info', {}).get('name', 'Student') if r.get('user_info') else 'Student',
            'skill': r.get('skill', ''),
            'score': round(r.get('score', 0)),
            'level': 'Advanced' if r.get('score', 0) >= 80 else ('Intermediate' if r.get('score', 0) >= 60 else 'Beginner'),
            'badge': 'Verified' if not r.get('gap_identified') else 'In Progress',
        } for r in top_results]
        return render_template('recruiter/recruiter_dashboard.html',
            total_candidates=total_candidates, total_verified=total_verified,
            avg_score=avg_score, my_jobs_count=my_jobs_count, top_candidates=top_candidates)

    @app.route('/recruiter/talent-search')
    def talent_discovery():
        if 'user_id' not in session or session.get('role') != 'recruiter':
            return redirect(url_for('login'))
        skill_filter = request.args.get('skill', '')
        level_filter = request.args.get('level', '')
        query = {'role': 'student'}
        if skill_filter:
            matched_ids  = results_col.distinct('user_id', {'skill': {'$regex': skill_filter, '$options': 'i'}})
            query['_id'] = {'$in': matched_ids}
        students   = list(users_col.find(query))
        candidates = []
        for s in students:
            for r in list(results_col.find({'user_id': s['_id']})):
                if skill_filter and skill_filter.lower() not in r.get('skill', '').lower():
                    continue
                level = 'Beginner' if r['score'] < 60 else ('Intermediate' if r['score'] < 80 else 'Advanced')
                if level_filter and level != level_filter:
                    continue
                candidates.append({'name': s.get('name', 'Student'), 'skill': r.get('skill', ''), 'score': r.get('score', 0), 'level': level})
        return render_template('recruiter/talent_discovery_search.html', candidates=candidates)

    @app.route('/recruiter/post-job', methods=['GET', 'POST'])
    def recruiter_post_job():
        if 'user_id' not in session or session.get('role') != 'recruiter':
            return redirect(url_for('login'))
        if request.method == 'POST':
            title    = request.form.get('title', '').strip()
            company  = request.form.get('company', '').strip()
            location = request.form.get('location', '').strip()
            job_type = request.form.get('type', 'Full-time')
            skills   = [s.strip() for s in request.form.get('skills', '').split(',') if s.strip()]
            desc     = request.form.get('description', '').strip()
            link     = request.form.get('link', '').strip()
            if title:
                db['jobs'].insert_one({
                    'title': title, 'company': company, 'location': location,
                    'type': job_type, 'required_skills': skills, 'description': desc,
                    'link': link, 'posted_by': ObjectId(session['user_id']),
                    'recruiter_name': session.get('name', 'Recruiter'),
                })
                flash(f'Job "{title}" posted successfully!', 'success')
                return redirect(url_for('recruiter_dashboard'))
            flash('Job title is required.', 'error')
        return render_template('recruiter/post_job.html')

    @app.route('/recruiter/my-jobs')
    def recruiter_my_jobs():
        if 'user_id' not in session or session.get('role') != 'recruiter':
            return redirect(url_for('login'))
        my_jobs = list(db['jobs'].find({'posted_by': ObjectId(session['user_id'])}).sort('_id', -1))
        return render_template('recruiter/my_jobs.html', jobs=my_jobs)

    @app.route('/recruiter/delete-job/<job_id>', methods=['POST'])
    def recruiter_delete_job(job_id):
        if 'user_id' not in session or session.get('role') != 'recruiter':
            return redirect(url_for('login'))
        db['jobs'].delete_one({'_id': ObjectId(job_id), 'posted_by': ObjectId(session['user_id'])})
        flash('Job removed.', 'success')
        return redirect(url_for('recruiter_my_jobs'))
