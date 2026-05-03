"""
routes/admin.py — Admin Routes
================================
Routes: /admin/dashboard, /admin/delete_user/<user_id>,
        /admin/add_question, /admin/delete_question/<q_id>,
        /admin/delete_post/<post_id>
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify
from bson.objectid import ObjectId


def register_admin(app, users_col, results_col, questions_col, db):
    """Register all admin routes on the Flask app."""

    @app.route('/admin/dashboard')
    def admin_dashboard():
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))

        total_users      = users_col.count_documents({})
        total_students   = users_col.count_documents({'role': 'student'})
        total_recruiters = users_col.count_documents({'role': 'recruiter'})
        total_tests      = results_col.count_documents({})
        avg_score_res    = list(results_col.aggregate([{'$group': {'_id': None, 'avg': {'$avg': '$score'}}}]))
        avg_score        = round(avg_score_res[0]['avg']) if avg_score_res else 0
        total_jobs       = db['jobs'].count_documents({})
        total_posts      = db['community_posts'].count_documents({})
        total_questions  = questions_col.count_documents({})
        all_users        = list(users_col.find({}, {'password': 0}).sort('_id', -1).limit(20))
        all_questions    = list(questions_col.find().sort('_id', -1).limit(30))
        all_posts        = list(db['community_posts'].find().sort('_id', -1).limit(20))
        recent_results   = list(results_col.find().sort('_id', -1).limit(10))

        for r in recent_results:
            u = users_col.find_one({'_id': r.get('user_id')}, {'name': 1})
            r['user_name'] = u.get('name', 'Unknown') if u else 'Unknown'

        skill_stats = list(results_col.aggregate([
            {'$group': {'_id': '$skill', 'count': {'$sum': 1}, 'avg': {'$avg': '$score'}}},
            {'$sort': {'count': -1}}, {'$limit': 8},
        ]))

        return render_template('admin/admin_dashboard.html',
            total_users=total_users, total_students=total_students,
            total_recruiters=total_recruiters, total_tests=total_tests,
            avg_score=avg_score, total_jobs=total_jobs,
            total_posts=total_posts, total_questions=total_questions,
            all_users=all_users, all_questions=all_questions,
            all_posts=all_posts, recent_results=recent_results,
            skill_stats=skill_stats)

    @app.route('/admin/delete_user/<user_id>', methods=['POST'])
    def admin_delete_user(user_id):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        users_col.delete_one({'_id': ObjectId(user_id)})
        flash('User deleted.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/add_question', methods=['POST'])
    def admin_add_question():
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        skill    = request.form.get('skill', '').strip()
        question = request.form.get('question', '').strip()
        opts     = [request.form.get(f'opt{i}', '').strip() for i in range(1, 5)]
        answer   = request.form.get('answer', '').strip()
        if skill and question and answer:
            questions_col.insert_one({'skill': skill, 'question': question, 'options': opts, 'answer': answer})
            flash('Question added!', 'success')
        else:
            flash('Please fill all required fields.', 'error')
        return redirect(url_for('admin_dashboard') + '#questions')

    @app.route('/admin/delete_question/<q_id>', methods=['POST'])
    def admin_delete_question(q_id):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        questions_col.delete_one({'_id': ObjectId(q_id)})
        flash('Question deleted.', 'success')
        return redirect(url_for('admin_dashboard') + '#questions')

    @app.route('/admin/delete_post/<post_id>', methods=['POST'])
    def admin_delete_post(post_id):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        db['community_posts'].delete_one({'_id': ObjectId(post_id)})
        flash('Post removed.', 'success')
        return redirect(url_for('admin_dashboard') + '#community')
