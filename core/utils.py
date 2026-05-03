# utils.py — GapLens helper functions
# Loads all API keys from .env automatically.

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from dotenv import load_dotenv
load_dotenv()  # Reads .env into os.environ


# ─────────────────────────────────────────────────────────────
#  DIAGNOSTIC SCORING (Rule-Based, no ML)
# ─────────────────────────────────────────────────────────────

def evaluate_score(answers, correct_answers):
    """
    Evaluates MCQ answers.
    Returns (score: float, gap_identified: bool).
    gap_identified = True when score < 60% — hard business rule.
    """
    if not answers or not correct_answers:
        return 0, True

    correct_count = sum(1 for i, ans in enumerate(answers) if ans == correct_answers[i])
    score = (correct_count / len(correct_answers)) * 100
    gap_identified = score < 60
    return score, gap_identified


# ─────────────────────────────────────────────────────────────
#  YOUTUBE VIDEO RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────

def fetch_youtube_videos(query, max_results=3):
    """
    Fetches top tutorial videos for a skill using YouTube Data API v3.
    API key is read from YOUTUBE_API_KEY in .env.
    Returns: list of {title, video_id, url, thumbnail}
    """
    from googleapiclient.discovery import build

    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("Warning: YOUTUBE_API_KEY not set in .env")
        return []

    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        response = youtube.search().list(
            q=f"{query} tutorial for beginners",
            part='snippet',
            type='video',
            maxResults=max_results,
            relevanceLanguage='en',
            safeSearch='moderate',
        ).execute()

        videos = []
        for item in response.get('items', []):
            snippet = item['snippet']
            videos.append({
                'title':     snippet['title'],
                'channel':   snippet['channelTitle'],
                'video_id':  item['id']['videoId'],
                'url':       f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'thumbnail': snippet['thumbnails']['medium']['url'],
            })
        return videos

    except Exception as e:
        print(f"Error fetching YouTube videos: {e}")
        return []


# ─────────────────────────────────────────────────────────────
#  GEMINI AI — SKILL GAP INSIGHTS
# ─────────────────────────────────────────────────────────────

def get_gemini_skill_insights(skill, score):
    """
    Uses the Gemini API (Google AI Studio) to generate a short,
    personalised insight paragraph about the student's skill gap.
    Falls back to a rule-based message if the API is unavailable.
    """
    import google.generativeai as genai

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        # Fallback rule-based message
        if score < 40:
            return f"Your {skill} score is critically low ({score:.0f}%). Focus on fundamentals first."
        elif score < 60:
            return f"You have a skill gap in {skill} ({score:.0f}%). Targeted practice will bridge this gap."
        else:
            return f"Good work on {skill} ({score:.0f}%)! Keep practising to reach mastery."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = (
            f"A student scored {score:.0f}% in a {skill} diagnostic test on the GapLens platform. "
            f"Write a concise 2-sentence personalised insight: what this score means and one actionable "
            f"next step. Keep the tone encouraging and professional. No bullet points."
        )
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"Score: {score:.0f}% in {skill}. Review core concepts and retake the assessment."


# ─────────────────────────────────────────────────────────────
#  PDF RESUME GENERATION + EMAIL
# ─────────────────────────────────────────────────────────────

def generate_and_email_pdf(user_data, recipient_email):
    """
    Generates a verified-skill PDF resume and emails it to the student.
    Requires: wkhtmltopdf installed, SENDER_EMAIL + SENDER_PASSWORD in .env.
    """
    import pdfkit

    skill_rows = "".join(
        f"<tr><td>{skill}</td><td>{score}%</td>"
        f"<td>{'✅ Verified' if score >= 60 else '⚠️ Gap Identified'}</td></tr>"
        for skill, score in user_data.get('verified_skills', {}).items()
    )

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        body {{ font-family: Arial, sans-serif; color: #1a1a2e; padding: 2rem; }}
        h1   {{ color: #006970; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
        th, td {{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }}
        th {{ background: #006970; color: #fff; }}
        .badge {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.85em; }}
      </style>
    </head>
    <body>
      <h1>GapLens Verified Resume</h1>
      <p><strong>Name:</strong> {user_data.get('name', 'Student')}</p>
      <p><strong>Email:</strong> {recipient_email}</p>
      <h2>Verified Skill Scores</h2>
      <table>
        <tr><th>Skill</th><th>Score</th><th>Status</th></tr>
        {skill_rows}
      </table>
      <p style="margin-top:2rem; font-size:0.8em; color:#888;">
        Generated by GapLens Diagnostic Platform — Scores are independently verified.
      </p>
    </body>
    </html>
    """

    pdf_path = f"resume_{user_data.get('name', 'student').replace(' ', '_')}.pdf"

    try:
        pdfkit.from_string(html_content, pdf_path)

        sender_email    = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('SENDER_PASSWORD')

        if not sender_email or not sender_password:
            print("Email creds not set — PDF saved locally.")
            return True

        msg = MIMEMultipart()
        msg['Subject'] = "Your Verified GapLens Resume 🎓"
        msg['From']    = sender_email
        msg['To']      = recipient_email
        msg.attach(MIMEText(
            "Congratulations!\n\nAttached is your GapLens-verified resume. "
            "Your skill scores are independently verified and ready to share with recruiters."
        ))

        with open(pdf_path, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename="GapLens_Resume.pdf")
            msg.attach(attach)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        return True

    except Exception as e:
        print(f"Error generating/emailing PDF: {e}")
        return False

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
