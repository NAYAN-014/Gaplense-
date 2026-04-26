from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from utils import evaluate_score, fetch_youtube_videos, generate_and_email_pdf, get_gemini_skill_insights

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'gaplens_dev_secret')

# ── MongoDB ───────────────────────────────────────────────────────────────────
client = MongoClient(os.environ.get('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['gaplens']
users_col     = db['users']
results_col   = db['test_results']
questions_col = db['questions']

# ── Google OAuth (Authlib) ────────────────────────────────────────────────────
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/drive.file'
    },
)


# ── AUTHENTICATION ROUTES ─────────────────────────────────────────────────────

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('username', '').strip()
        password   = request.form.get('password', '')
        # Search by email OR username field
        user = users_col.find_one({'$or': [{'email': identifier}, {'username': identifier}]})
        if user and user.get('password') == password:
            session['user_id'] = str(user['_id'])
            session['role']    = user.get('role', 'student')
            session['name']    = user.get('name', 'User')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please check your email/username and password.', 'error')
    return render_template('auth/login_page.html')



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

        users_col.insert_one({'name': name, 'email': email, 'password': password, 'role': role})
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── GOOGLE OAUTH ROUTES ───────────────────────────────────────────────────────

@app.route('/auth/google')
def google_login():
    """Redirects user to Google's OAuth consent screen."""
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def google_callback():
    """Handles the Google OAuth callback, creates/updates user in DB."""
    token = google.authorize_access_token()
    user_info = token.get('userinfo')

    if not user_info:
        flash('Google login failed. Please try again.', 'error')
        return redirect(url_for('login'))

    email = user_info['email']
    name  = user_info.get('name', email)

    # Upsert the user — first login creates the account automatically
    existing = users_col.find_one({'email': email})
    if not existing:
        result = users_col.insert_one({
            'name':         name,
            'email':        email,
            'password':     None,           # Google users have no local password
            'role':         'student',      # default role; admin can change later
            'google_id':    user_info['sub'],
            'avatar':       user_info.get('picture', ''),
        })
        user_id = str(result.inserted_id)
        role    = 'student'
    else:
        user_id = str(existing['_id'])
        role    = existing.get('role', 'student')
        # Refresh name/avatar in case they changed
        users_col.update_one({'_id': existing['_id']}, {'$set': {
            'name':   name,
            'avatar': user_info.get('picture', ''),
        }})

    session['user_id']       = user_id
    session['role']          = role
    session['name']          = name
    session['google_token']  = token.get('access_token')  # stored for Drive API calls

    return redirect(url_for('index'))


# ── DASHBOARD ROUTES ──────────────────────────────────────────────────────────

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    uid = ObjectId(session['user_id'])
    user = users_col.find_one({'_id': uid})
    results = list(results_col.find({'user_id': uid}))
    recs = [{'skill':r['skill'],'score':r['score'],
             'level':'Beginner' if r['score']<60 else('Intermediate' if r['score']<80 else 'Advanced')}
            for r in results]
    trending = list(results_col.aggregate([
        {'$group':{'_id':'$skill','attempts':{'$sum':1},'avg_score':{'$avg':'$score'}}},
        {'$sort':{'attempts':-1}},{'$limit':5}]))
    posts = list(db['community_posts'].find().sort('_id',-1).limit(4))
    return render_template('student/student_dashboard.html',
        user=user,results=results,recs=recs,trending=trending,posts=posts)


@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    if 'user_id' not in session or session.get('role')!='student':
        return redirect(url_for('login'))
    user = users_col.find_one({'_id':ObjectId(session['user_id'])})
    if request.method=='POST':
        upd={'name':request.form.get('name',user.get('name')),
             'college':request.form.get('college',''),
             'skills':request.form.get('skills','').split(','),
             'bio':request.form.get('bio',''),
             'linkedin':request.form.get('linkedin','')}
        users_col.update_one({'_id':ObjectId(session['user_id'])},{'$set':upd})
        session['name']=upd['name']
        flash('Profile updated!','success')
        return redirect(url_for('student_dashboard'))
    return render_template('student/edit_profile.html',user=user)

@app.route('/jobs')
def jobs():
    if 'user_id' not in session or session.get('role')!='student':
        return redirect(url_for('login'))
    verified=[r['skill'] for r in results_col.find({'user_id':ObjectId(session['user_id']),'gap_identified':False})]
    listings=list(db['jobs'].find({'required_skills':{'$in':verified}})) if verified else []
    return render_template('student/jobs.html',jobs=listings,skills=verified)

@app.route('/video_recommendations')
def video_recommendations():
    if 'user_id' not in session or session.get('role')!='student':
        return redirect(url_for('login'))
    gaps=list(results_col.find({'user_id':ObjectId(session['user_id']),'gap_identified':True}))
    all_videos={g['skill']:fetch_youtube_videos(g['skill']) for g in gaps}
    return render_template('student/video_recommendations.html',all_videos=all_videos)

@app.route('/learning_hub')
def learning_hub():
    if 'user_id' not in session or session.get('role')!='student':
        return redirect(url_for('login'))
    results=list(results_col.find({'user_id':ObjectId(session['user_id'])}))
    recs=[{'skill':r['skill'],'score':r['score'],
           'level':'Beginner' if r['score']<60 else('Intermediate' if r['score']<80 else 'Advanced')}
          for r in results]
    return render_template('student/learning_hub.html',recs=recs)

@app.route('/insights_panel')
def insights_panel():
    if 'user_id' not in session or session.get('role')!='student':
        return redirect(url_for('login'))
    trending=list(results_col.aggregate([
        {'$group':{'_id':'$skill','attempts':{'$sum':1},'avg_score':{'$avg':'$score'}}},
        {'$sort':{'attempts':-1}},{'$limit':10}]))
    return render_template('student/insights_panel.html',trending=trending)

@app.route('/community')
def community():
    if 'user_id' not in session: return redirect(url_for('login'))
    posts=list(db['community_posts'].find().sort('_id',-1).limit(20))
    return render_template('student/community.html',posts=posts)

@app.route('/community/post',methods=['POST'])
def community_post():
    if 'user_id' not in session: return redirect(url_for('login'))
    c=request.form.get('content','').strip()
    if c:
        db['community_posts'].insert_one({'user_id':ObjectId(session['user_id']),
            'author':session.get('name','Student'),'content':c})
    return redirect(url_for('community'))

@app.route('/skill_gap_analysis')
def skill_gap_analysis():
    if 'user_id' not in session or session.get('role')!='student':
        return redirect(url_for('login'))
    results=list(results_col.find({'user_id':ObjectId(session['user_id'])}))
    return render_template('student/skill_gap_analysis.html',
        gaps=[r for r in results if r.get('gap_identified')],
        mastered=[r for r in results if not r.get('gap_identified')])

@app.route('/profile_management')
def profile_management():
    if 'user_id' not in session or session.get('role')!='student':
        return redirect(url_for('login'))
    user=users_col.find_one({'_id':ObjectId(session['user_id'])})
    results=list(results_col.find({'user_id':ObjectId(session['user_id'])}))
    return render_template('student/profile_management.html',
        user=user,results=results,badges=user.get('badges',[]))

@app.route('/award_badge',methods=['POST'])
def award_badge():
    if 'user_id' not in session or session.get('role')!='student':
        return jsonify({'error':'Unauthorized'}),401
    data=request.json; skill=data.get('skill'); score=data.get('score',0)
    if score>=60:
        badge={'skill':skill,'score':score,'level':'Verified' if score>=80 else 'Certified'}
        users_col.update_one({'_id':ObjectId(session['user_id'])},{'$addToSet':{'badges':badge}})
        return jsonify({'awarded':True,'badge':badge})
    return jsonify({'awarded':False})



@app.route('/student/profile')
def student_profile():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    user    = users_col.find_one({'_id': ObjectId(session['user_id'])})
    results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
    return render_template('student/student_profile_page.html', user=user, results=results)


@app.route('/student/skill-map')
def skill_map():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
    return render_template('student/skill_map_visualization.html', results=results)


@app.route('/student/insights')
def deep_insights():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
    return render_template('student/deep_insights_analytics.html', results=results)


@app.route('/student/assessments')
def test_selection():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    results = list(results_col.find({'user_id': ObjectId(session['user_id'])}))
    return render_template('test/test_selection_1.html', results=results)



@app.route('/student/resources')
def curated_resources():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student/curated_resources_library.html')


@app.route('/recruiter/dashboard')
def recruiter_dashboard():
    if 'user_id' not in session or session.get('role') != 'recruiter':
        return redirect(url_for('login'))
    # Real stats
    total_candidates = users_col.count_documents({'role': 'student'})
    total_verified   = results_col.count_documents({'gap_identified': False})
    avg_res = list(results_col.aggregate([{'$group':{'_id':None,'avg':{'$avg':'$score'}}}]))
    avg_score = round(avg_res[0]['avg']) if avg_res else 0
    my_jobs_count = db['jobs'].count_documents({'posted_by': ObjectId(session['user_id'])})
    # Top candidates (highest scores)
    top_results = list(results_col.aggregate([
        {'$sort': {'score': -1}},
        {'$limit': 10},
        {'$lookup': {'from':'users','localField':'user_id','foreignField':'_id','as':'user_info'}},
        {'$unwind': {'path':'$user_info','preserveNullAndEmptyArrays': True}},
    ]))
    top_candidates = []
    for r in top_results:
        top_candidates.append({
            'name': r.get('user_info',{}).get('name','Student') if r.get('user_info') else 'Student',
            'skill': r.get('skill',''),
            'score': round(r.get('score',0)),
            'level': 'Advanced' if r.get('score',0)>=80 else ('Intermediate' if r.get('score',0)>=60 else 'Beginner'),
            'badge': 'Verified' if not r.get('gap_identified') else 'In Progress'
        })
    return render_template('recruiter/recruiter_dashboard.html',
        total_candidates=total_candidates, total_verified=total_verified,
        avg_score=avg_score, my_jobs_count=my_jobs_count,
        top_candidates=top_candidates)


@app.route('/recruiter/talent-search')
def talent_discovery():
    if 'user_id' not in session or session.get('role') != 'recruiter':
        return redirect(url_for('login'))
    skill_filter = request.args.get('skill', '')
    level_filter = request.args.get('level', '')
    query = {'role': 'student'}
    # Build list of candidates from results
    if skill_filter:
        matched_ids = results_col.distinct('user_id', {'skill': {'$regex': skill_filter, '$options': 'i'}})
        query['_id'] = {'$in': matched_ids}
    students = list(users_col.find(query))
    # Join with test results
    candidates = []
    for s in students:
        user_results = list(results_col.find({'user_id': s['_id']}))
        for r in user_results:
            if skill_filter and skill_filter.lower() not in r.get('skill','').lower():
                continue
            level = 'Beginner' if r['score']<60 else ('Intermediate' if r['score']<80 else 'Advanced')
            if level_filter and level != level_filter:
                continue
            candidates.append({'name': s.get('name','Student'), 'skill': r.get('skill',''), 'score': r.get('score',0), 'level': level})
    return render_template('recruiter/talent_discovery_search.html', candidates=candidates)



@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    total_users   = users_col.count_documents({})
    total_students = users_col.count_documents({'role':'student'})
    total_recruiters = users_col.count_documents({'role':'recruiter'})
    total_tests   = results_col.count_documents({})
    avg_score_res = list(results_col.aggregate([{'$group':{'_id':None,'avg':{'$avg':'$score'}}}]))
    avg_score     = round(avg_score_res[0]['avg']) if avg_score_res else 0
    total_jobs    = db['jobs'].count_documents({})
    total_posts   = db['community_posts'].count_documents({})
    total_questions = questions_col.count_documents({})
    all_users     = list(users_col.find({}, {'password':0}).sort('_id',-1).limit(20))
    all_questions = list(questions_col.find().sort('_id',-1).limit(30))
    all_posts     = list(db['community_posts'].find().sort('_id',-1).limit(20))
    recent_results = list(results_col.find().sort('_id',-1).limit(10))
    # Enrich results with user names
    for r in recent_results:
        u = users_col.find_one({'_id': r.get('user_id')}, {'name':1})
        r['user_name'] = u.get('name','Unknown') if u else 'Unknown'
    skill_stats = list(results_col.aggregate([
        {'$group':{'_id':'$skill','count':{'$sum':1},'avg':{'$avg':'$score'}}},
        {'$sort':{'count':-1}},{'$limit':8}]))
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
        return jsonify({'error':'Unauthorized'}), 401
    users_col.delete_one({'_id': ObjectId(user_id)})
    flash('User deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/add_question', methods=['POST'])
def admin_add_question():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error':'Unauthorized'}), 401
    skill   = request.form.get('skill','').strip()
    question = request.form.get('question','').strip()
    opts    = [request.form.get(f'opt{i}','').strip() for i in range(1,5)]
    answer  = request.form.get('answer','').strip()
    if skill and question and answer:
        questions_col.insert_one({'skill':skill,'question':question,'options':opts,'answer':answer})
        flash('Question added!', 'success')
    else:
        flash('Please fill all required fields.', 'error')
    return redirect(url_for('admin_dashboard') + '#questions')


@app.route('/admin/delete_question/<q_id>', methods=['POST'])
def admin_delete_question(q_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error':'Unauthorized'}), 401
    questions_col.delete_one({'_id': ObjectId(q_id)})
    flash('Question deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#questions')


@app.route('/admin/delete_post/<post_id>', methods=['POST'])
def admin_delete_post(post_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error':'Unauthorized'}), 401
    db['community_posts'].delete_one({'_id': ObjectId(post_id)})
    flash('Post removed.', 'success')
    return redirect(url_for('admin_dashboard') + '#community')


# ── RECRUITER JOB POSTING ─────────────────────────────────────────────────────

@app.route('/recruiter/post-job', methods=['GET','POST'])
def recruiter_post_job():
    if 'user_id' not in session or session.get('role') != 'recruiter':
        return redirect(url_for('login'))
    if request.method == 'POST':
        title    = request.form.get('title','').strip()
        company  = request.form.get('company','').strip()
        location = request.form.get('location','').strip()
        job_type = request.form.get('type','Full-time')
        skills   = [s.strip() for s in request.form.get('skills','').split(',') if s.strip()]
        desc     = request.form.get('description','').strip()
        link     = request.form.get('link','').strip()
        if title:
            db['jobs'].insert_one({
                'title': title, 'company': company, 'location': location,
                'type': job_type, 'required_skills': skills,
                'description': desc, 'link': link,
                'posted_by': ObjectId(session['user_id']),
                'recruiter_name': session.get('name','Recruiter')
            })
            flash(f'Job "{title}" posted successfully!', 'success')
            return redirect(url_for('recruiter_dashboard'))
        flash('Job title is required.', 'error')
    return render_template('recruiter/post_job.html')


@app.route('/recruiter/my-jobs')
def recruiter_my_jobs():
    if 'user_id' not in session or session.get('role') != 'recruiter':
        return redirect(url_for('login'))
    my_jobs = list(db['jobs'].find({'posted_by': ObjectId(session['user_id'])}).sort('_id',-1))
    return render_template('recruiter/my_jobs.html', jobs=my_jobs)


@app.route('/recruiter/delete-job/<job_id>', methods=['POST'])
def recruiter_delete_job(job_id):
    if 'user_id' not in session or session.get('role') != 'recruiter':
        return redirect(url_for('login'))
    db['jobs'].delete_one({'_id': ObjectId(job_id), 'posted_by': ObjectId(session['user_id'])})
    flash('Job removed.', 'success')
    return redirect(url_for('recruiter_my_jobs'))


# ── COMMUNITY COMMENTS ────────────────────────────────────────────────────────

@app.route('/community/comment/<post_id>', methods=['POST'])
def community_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    text = request.form.get('comment','').strip()
    if text:
        comment = {
            'author': session.get('name','User'),
            'role':   session.get('role','student'),
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
    # Allow: admin or post author
    if post and (session.get('role') == 'admin' or str(post.get('user_id')) == session['user_id']):
        db['community_posts'].delete_one({'_id': ObjectId(post_id)})
        flash('Post removed.', 'success')
    return redirect(url_for('community'))


# ── DIAGNOSTIC ENGINE ─────────────────────────────────────────────────────────

@app.route('/diagnostic/<skill>', methods=['GET'])
def diagnostic_assessment(skill):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    pipeline = [{'$match': {'skill': skill}}, {'$sample': {'size': 5}}]
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

    insight = get_gemini_skill_insights(skill, score)

    results_col.insert_one({
        'user_id':       ObjectId(session['user_id']),
        'skill':         skill,
        'score':         score,
        'gap_identified': gap_identified,
        'insight':       insight,
    })

    return jsonify({
        'score':         score,
        'gap_identified': gap_identified,
        'insight':       insight,
        'redirect':      url_for('results_recommendations', skill=skill),
    })


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


# ── RESUME GENERATION ─────────────────────────────────────────────────────────

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('profile_management'))

    user = users_col.find_one({'_id': ObjectId(session['user_id'])})
    raw  = results_col.find({'user_id': ObjectId(session['user_id'])})
    verified_skills = {r['skill']: round(r['score']) for r in raw}

    user_data = {'name': user.get('name', 'Student'), 'verified_skills': verified_skills}
    success   = generate_and_email_pdf(user_data, user.get('email'))

    if success:
        flash('Resume generated and emailed to you!', 'success')
    else:
        flash('Resume generation failed. Please try again.', 'error')
    return redirect(url_for('profile_management'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)


