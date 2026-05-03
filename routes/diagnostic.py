"""
routes/diagnostic.py — Diagnostic / Test Engine Routes
========================================================
Routes: /diagnostic/<skill>, /diagnostic/submit
"""

from flask import render_template, request, redirect, url_for, session, jsonify
from bson.objectid import ObjectId
from core.utils import evaluate_score, get_gemini_skill_insights


def register_diagnostic(app, users_col, results_col, questions_col, db):
    """Register all diagnostic / test engine routes on the Flask app."""

    @app.route('/diagnostic/<skill>', methods=['GET'])
    def diagnostic_assessment(skill):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        pipeline  = [{'$match': {'skill': skill}}, {'$sample': {'size': 5}}]
        questions = list(questions_col.aggregate(pipeline))
        return render_template('test/diagnostic_assessment.html', skill=skill, questions=questions)

    @app.route('/diagnostic/submit', methods=['POST'])
    def submit_diagnostic():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        data            = request.json
        skill           = data.get('skill')
        answers         = data.get('answers')
        correct_answers = data.get('correct_answers')

        score, gap_identified = evaluate_score(answers, correct_answers)
        insight               = get_gemini_skill_insights(skill, score)

        results_col.insert_one({
            'user_id':        ObjectId(session['user_id']),
            'skill':          skill,
            'score':          score,
            'gap_identified': gap_identified,
            'insight':        insight,
        })

        return jsonify({
            'score':          score,
            'gap_identified': gap_identified,
            'insight':        insight,
            'redirect':       url_for('results_recommendations', skill=skill),
        })
