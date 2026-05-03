# GapLens Skill Diagnostic Platform — Comprehensive Project Documentation

---

## 1. Project Overview

**GapLens** is a full-stack web application that bridges the gap between academic learning and industry employment. It provides a three-sided marketplace:

| Role | Purpose |
|------|---------|
| **Student** | Takes skill diagnostics, receives personalized learning recommendations, builds verified resumes, and applies to matched jobs |
| **Recruiter** | Posts jobs with required skills, discovers verified talent through diagnostic scores |
| **Admin** | Manages platform content (MCQ questions), monitors users, moderates community posts |

The platform uses **objective, test-based verification** instead of self-reported skills, making it valuable for both learners and employers.

---

## 2. Core Objectives

1. **Accurate Skill Assessment** — Dynamic, randomized 5-question MCQ diagnostics per skill domain
2. **Gap Identification** — Scores below 60% automatically flag a skill gap
3. **Targeted Learning** — YouTube API integration fetches tutorial videos for identified gaps
4. **Verified Talent Pool** — Recruiters filter candidates by proven test scores, not resumes alone
5. **Professional Resume Generation** — Auto-generated PDF resumes emailed to students based on verified scores
6. **Resume Upload** — Students can upload their own PDF/DOC/DOCX resumes via GridFS or link Google Drive
7. **Job Matching** — All recruiter jobs visible to students, with best matches prioritized

---

## 3. Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Core language |
| Flask | 2.x | Web framework & routing |
| PyMongo | 4.x | MongoDB driver |
| python-dotenv | 1.x | Environment variable management |
| Werkzeug | 2.x | Security utilities (password hashing, file handling) |
| Authlib | 1.x | Google OAuth 2.0 integration |
| GridFS | Built-in | Binary file storage in MongoDB |

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML5 | Semantic markup |
| CSS3 | Custom styling (Glassmorphism, Bento Grid) |
| JavaScript (Vanilla) | Interactivity, theme toggle, AJAX diagnostics |
| Jinja2 | Server-side templating |
| Tailwind CSS (CDN) | Utility-first styling framework |
| Google Fonts | Inter & Space Grotesk typography |
| Material Symbols | Iconography |

### Database
| Technology | Purpose |
|------------|---------|
| MongoDB | Document-oriented NoSQL database |
| GridFS | Store resume files (PDF, DOC, DOCX) |

### External APIs
| API | Purpose |
|-----|---------|
| YouTube Data API v3 | Fetch tutorial videos for skill gaps |
| Google Gemini API | Generate personalized skill insights |
| Google OAuth 2.0 | Social login with Drive file scope |
| Gmail SMTP | Send generated PDF resumes via email |

---

## 4. System Architecture

```
┌─────────────────┐     HTTP      ┌──────────────────┐     ┌─────────────────┐
│   Web Browser   │ ◄──────────►  │  Flask Server    │ ◄──►│   MongoDB       │
│  (Student/      │   GET/POST    │  (Python 3)      │     │  + GridFS       │
│  Recruiter/     │               │                  │     │                 │
│  Admin)         │               │  • Routes        │     │  • users        │
└─────────────────┘               │  • Auth          │     │  • test_results │
                                  │  • Business Logic│     │  • questions    │
                                  │                  │     │  • jobs         │
                                  │  External APIs:  │     │  • community    │
                                  │  • YouTube       │     │  • fs.files     │
                                  │  • Gemini        │     │  • fs.chunks    │
                                  │  • Google OAuth  │     └─────────────────┘
                                  │  • Gmail SMTP    │
                                  └──────────────────┘
```

### Request Flow
1. User interacts with the Jinja2-rendered HTML interface
2. Browser sends HTTP request to Flask route
3. Flask authenticates via session cookies
4. Business logic queries MongoDB or external APIs
5. Flask renders template with data and returns HTML response

---

## 5. Database Schema (MongoDB Collections)

### 5.1 `users` Collection
```json
{
  "_id": ObjectId("..."),
  "name": "John Doe",
  "email": "john@example.com",
  "password": "plaintext_or_hashed",
  "role": "student | recruiter | admin",
  "college": "Stanford University",
  "skills": ["Python", "JavaScript"],
  "bio": "Aspiring full-stack developer",
  "linkedin": "https://linkedin.com/in/john",
  "google_drive_resume_link": "https://drive.google.com/...",
  "uploaded_resume_id": ObjectId("..."),
  "uploaded_resume_filename": "john_resume.pdf",
  "uploaded_resume_date": ISODate("2024-..."),
  "badges": [
    {"skill": "Python", "score": 85, "level": "Verified"}
  ],
  "google_id": "...",
  "avatar": "https://..."
}
```

### 5.2 `test_results` Collection
```json
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("..."),
  "skill": "Python",
  "score": 72.5,
  "gap_identified": false,
  "insight": "Good work on Python...",
  "timestamp": ISODate("2024-...")
}
```

### 5.3 `questions` Collection
```json
{
  "_id": ObjectId("..."),
  "skill": "Python",
  "question": "What does enumerate() return?",
  "options": ["A list", "A dict", "An enumerate object", "A tuple"],
  "answer": "An enumerate object"
}
```

### 5.4 `jobs` Collection
```json
{
  "_id": ObjectId("..."),
  "title": "Python Backend Developer",
  "company": "TechCorp",
  "location": "Bangalore / Remote",
  "type": "Full-time",
  "required_skills": ["Python", "Django", "SQL"],
  "description": "...",
  "link": "https://...",
  "posted_by": ObjectId("..."),
  "recruiter_name": "Jane Smith"
}
```

### 5.5 `community_posts` Collection
```json
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("..."),
  "author": "John Doe",
  "content": "Just completed my Python assessment!",
  "comments": [
    {"author": "Jane", "role": "student", "text": "Congrats!"}
  ]
}
```

### 5.6 GridFS (`fs.files` & `fs.chunks`)
Stores binary resume files with metadata:
```json
// fs.files
{
  "_id": ObjectId("..."),
  "filename": "resume.pdf",
  "contentType": "application/pdf",
  "length": 245760,
  "uploadDate": ISODate("2024-..."),
  "metadata": {
    "user_id": ObjectId("...")
  }
}
```

---

## 6. API Endpoints Reference

### 6.1 Authentication
| Method | Route | Description |
|--------|-------|-------------|
| GET/POST | `/login` | Standard email/password login |
| GET/POST | `/signup` | User registration |
| GET | `/logout` | Clear session |
| GET | `/auth/google` | Initiate Google OAuth |
| GET | `/auth/google/callback` | Google OAuth callback |

### 6.2 Student Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/student/dashboard` | Student dashboard with stats |
| GET | `/student/profile` | Profile page with resume upload |
| GET/POST | `/edit_profile` | Edit personal info + Google Drive link |
| GET | `/jobs` | All recruiter jobs (matched first) |
| GET | `/video_recommendations` | YouTube videos for gaps |
| GET | `/learning_hub` | Learning resources |
| GET | `/insights_panel` | Market trends |
| GET | `/community` | Community feed |
| POST | `/community/post` | Create post |
| GET | `/skill_gap_analysis` | Gap vs mastered skills |
| GET | `/profile_management` | Resume page with upload banner |
| POST | `/award_badge` | Award skill badge (AJAX) |
| GET | `/student/skill-map` | Skill visualization |
| GET | `/student/insights` | Deep analytics |
| GET | `/student/assessments` | Test selection |
| GET | `/student/resources` | Curated resources |
| POST | `/upload-resume` | Upload PDF/DOC/DOCX to GridFS |
| GET | `/download-resume` | Download uploaded resume |
| POST | `/delete-resume` | Remove uploaded resume |
| POST | `/generate-resume` | Generate & email PDF resume |

### 6.3 Recruiter Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/recruiter/dashboard` | Recruiter stats & top candidates |
| GET | `/recruiter/talent-search` | Filter candidates by skill/level |
| GET/POST | `/recruiter/post-job` | Create job posting |
| GET | `/recruiter/my-jobs` | View own job postings |
| POST | `/recruiter/delete-job/<id>` | Remove a job posting |

### 6.4 Admin Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/admin/dashboard` | Platform overview & stats |
| POST | `/admin/delete_user/<id>` | Delete any user |
| POST | `/admin/add_question` | Add MCQ to database |
| POST | `/admin/delete_question/<id>` | Remove MCQ |
| POST | `/admin/delete_post/<id>` | Moderate community |

### 6.5 Diagnostic Engine
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/diagnostic/<skill>` | Take 5-question test |
| POST | `/diagnostic/submit` | Submit answers (AJAX) |
| GET | `/recommendations/<skill>` | View results & videos |

### 6.6 Community
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/community/comment/<post_id>` | Add comment |
| POST | `/community/delete/<post_id>` | Delete own/admin post |

---

## 7. Feature Modules (Detailed)

### 7.1 Multi-Role Authentication
- **Standard Login**: Email/username + password (plaintext comparison for now)
- **Google OAuth 2.0**: One-click login with `openid email profile drive.file` scopes
- **Role-based Access Control**: Routes check `session['role']` before serving content
- **Session Management**: Flask server-side sessions with secret key

### 7.2 Diagnostic Engine
- Fetches 5 random MCQs per skill from `questions` collection
- Evaluates answers: `(correct / total) * 100`
- **Gap Rule**: Score < 60% → `gap_identified = True`
- Generates AI insight via Gemini API (fallback to rule-based message)
- Stores result in `test_results` with skill, score, gap flag, and insight

### 7.3 Video Recommendations
- For every skill where `gap_identified == True`
- Queries YouTube Data API: `"{skill} tutorial for beginners"`
- Returns top 3 videos with title, channel, thumbnail, and URL

### 7.4 Resume System (Dual Mode)

#### A. AI-Generated Resume
- Collects all verified skills (score ≥ 60%) from `test_results`
- Generates HTML resume with skill table
- Converts to PDF using `pdfkit` + `wkhtmltopdf`
- Emails PDF to student via Gmail SMTP

#### B. Student-Uploaded Resume
- **Upload**: `POST /upload-resume` accepts PDF/DOC/DOCX (max 5 MB)
- **Storage**: GridFS in MongoDB (not filesystem)
- **Validation**: Extension check + size limit
- **Auto-replace**: New upload deletes old GridFS file
- **Download**: `GET /download-resume` serves file from GridFS
- **Remove**: `POST /delete-resume` clears GridFS + user record

#### C. Google Drive Link
- Field in Edit Profile: `google_drive_resume_link`
- Displayed as clickable button on Profile page

### 7.5 Job Board & Matching
- Recruiters post jobs with `required_skills` array
- **Old behavior**: Only showed jobs matching verified skills
- **New behavior**: Shows ALL jobs, sorted with matches first
- **Visual cues**:
  - Green left border + "Best Match" badge for matched jobs
  - Matching skill chips highlighted in cyan
  - Non-matching skills shown in default gray

### 7.6 Talent Discovery (Recruiter)
- Filter students by skill name (regex search)
- Filter by proficiency level: Beginner (<60%), Intermediate (60-79%), Advanced (≥80%)
- Shows candidate name, skill, score, and computed level

### 7.7 Admin Control Panel
- Platform statistics: total users, tests, jobs, posts, questions
- User management: view all users, delete accounts
- Question management: add MCQs with 4 options + correct answer
- Community moderation: delete inappropriate posts

---

## 8. Environment Variables (`.env`)

Create a `.env` file in the project root:

```env
# Flask
FLASK_SECRET_KEY=your-secret-key-here

# MongoDB
MONGO_URI=mongodb://localhost:27017/

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# YouTube Data API
YOUTUBE_API_KEY=your-youtube-api-key

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Email (Gmail SMTP)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

---

## 9. Installation & Setup Guide

### Prerequisites
- Python 3.10+
- MongoDB (local or Atlas)
- wkhtmltopdf (for PDF generation)

### Step 1: Clone & Navigate
```bash
git clone <repository-url>
cd gaplens
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Step 5: Seed Database (Optional)
```bash
python seed_questions.py
```

### Step 6: Run Application
```bash
python app.py
```
Access at: `http://localhost:5000`

---

## 10. Default Admin Credentials

The platform automatically creates a default admin account on first run:

| Field | Value |
|-------|-------|
| **Email** | `gaplensvip@gmail.com` |
| **Password** | `vip@123` |
| **Role** | `admin` |
| **Name** | `GapLens Admin` |

> **Security Note**: Change the default admin password immediately after first deployment in production.

### How to Login as Admin
1. Go to `/login`
2. Enter email: `gaplensvip@gmail.com`
3. Enter password: `vip@123`
4. You will be redirected to `/admin/dashboard`

---

## 11. Data Types Used

| Type | Usage Examples |
|------|---------------|
| **Integer** | Test scores, counts, IDs |
| **Float** | Percentage scores, averages |
| **String** | Names, emails, passwords, descriptions |
| **Boolean** | `gap_identified`, role flags |
| **Array/List** | Skills array, options array, comments |
| **Object/Dictionary** | MongoDB documents, badge objects, comment objects |
| **ObjectId** | MongoDB primary keys, foreign references |
| **ISODate** | Timestamps for uploads, test results |
| **Binary** | GridFS file chunks |

---

## 12. Security Considerations

1. **Password Storage**: Currently stores passwords in plaintext. Recommended: implement `werkzeug.security` hashing
2. **File Uploads**: Restricted to PDF/DOC/DOCX, max 5 MB, stored in GridFS (not filesystem)
3. **Session Security**: Uses Flask secret key; configure HTTPS in production
4. **Input Validation**: Basic validation on forms; sanitize user-generated content
5. **Admin Access**: Hard-coded seed admin; implement role-based middleware
6. **API Keys**: Stored in `.env` file, never committed to version control

---

## 13. Future Enhancements

- **Machine Learning**: Predictive analytics for career trajectories (currently rule-based only)
- **Real-time Chat**: WebSocket-based messaging between recruiters and students
- **LinkedIn Integration**: Auto-import skills and certifications
- **Course Integrations**: Coursera, Udemy API for structured learning paths
- **AI Interview Bot**: Gemini-powered mock interviews
- **Mobile App**: React Native or Flutter companion app
- **Payment Gateway**: Premium verified badges or recruiter subscriptions

---

## 14. Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB connection failed | Verify `MONGO_URI` in `.env`; ensure MongoDB service is running |
| PDF generation fails | Install `wkhtmltopdf` and add to system PATH |
| Google OAuth error | Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`; verify redirect URI in Google Console |
| YouTube videos not loading | Verify `YOUTUBE_API_KEY` has YouTube Data API v3 enabled |
| Email not sending | Use Gmail App Password, not regular password; enable Less Secure Apps or 2FA + App Password |
| Resume upload fails | Check file size (< 5 MB) and extension (PDF/DOC/DOCX) |

---

## 15. Contributors & License

- **Project**: GapLens Skill Diagnostic Platform
- **Purpose**: Academic / Portfolio Project
- **License**: MIT (recommended)

---

*Last Updated: 2024*

