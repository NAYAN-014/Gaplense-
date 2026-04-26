# Project Documentation: GapLens Skill Diagnostic Platform

## 1. Introduction
The **GapLens Skill Diagnostic Platform** is a modern, web-based SaaS (Software as a Service) application designed to bridge the gap between academic learning and industry requirements. 

It solves a critical problem in the current job market: students often do not know which specific skills they lack for their desired roles, and recruiters struggle to find verified, competent talent. GapLens addresses this by providing students with dynamic diagnostic assessments that identify their weak points and automatically recommending curated educational content to help them upskill. Simultaneously, it provides recruiters with a verified pool of talent.

This project is important because it creates a mutually beneficial ecosystem where continuous learning is directly tied to employability, empowering individuals to take charge of their careers.

## 2. Objectives
- **Accurate Assessment:** To evaluate user skills precisely through dynamic, randomized diagnostic testing.
- **Personalized Learning:** To provide targeted educational resources (via YouTube integration) tailored to bridge specific, identified skill gaps.
- **Talent Verification:** To connect recruiters with qualified candidates based on objective, tested skill profiles rather than just self-reported resumes.
- **Progress Tracking:** To offer a comprehensive, visually engaging dashboard for users to track their learning journey and analytics over time.

## 3. Technologies Used

### Frontend:
- **Languages:** HTML5, CSS3, JavaScript (Vanilla)
- **Design Approach:** Custom Glassmorphism UI, Responsive Web Design
- **Frameworks/Libraries:** Chart.js (for analytics visualization), FontAwesome (for iconography)

### Backend:
- **Language:** Python 3
- **Framework:** Flask (A lightweight WSGI web application framework)

### Database:
- **Type:** NoSQL (Document-oriented database)
- **Name:** MongoDB

## 4. Libraries & Tools Used
- **Flask:** The core backend web framework used for routing and API endpoints.
- **PyMongo:** The official Python driver used to interact with the MongoDB database.
- **python-dotenv:** Used for loading and managing environment variables securely.
- **werkzeug.security:** Used for hashing passwords and verifying user authentication securely.
- **google-api-python-client:** Utilized to fetch targeted educational video recommendations from the YouTube Data API.
- **google-generativeai:** Integrated to leverage AI models for dynamic content generation (like diagnostic questions).
- **pdfkit:** Used to generate dynamic, downloadable PDF reports and resumes for users.
- **requests:** Used to make external HTTP calls to third-party services.

## 5. System Architecture
The application follows a standard Client-Server architecture:
1. **Frontend (Client):** The user interacts with the HTML/CSS/JS interface in their web browser.
2. **Request:** When an action is taken (e.g., submitting a test), the frontend sends an HTTP GET or POST request to the backend server.
3. **Backend (Server):** The Flask application receives the request, processes the business logic, and communicates with the database or external APIs (like YouTube).
4. **Database:** MongoDB reads or writes the requested data (user profiles, test scores).
5. **Response:** The backend dynamically renders the appropriate HTML template with the new data and sends it back to the frontend for the user to view.

## 6. Features of the Project
- **Multi-Role Authentication:** Secure login and registration for Admins, Students, and Recruiters.
- **Dynamic Diagnostic Assessments:** Adaptive tests that evaluate specific technical skills.
- **Automated Video Recommendations:** YouTube API integration that suggests videos based specifically on a user's failed questions or skill gaps.
- **Interactive Skill Maps:** Visual data representations of a user's strengths and weaknesses.
- **Recruiter Job Board:** A portal for recruiters to post jobs and define required skill thresholds.
- **Talent Discovery Search:** Allows recruiters to filter and find students who meet their specific technical criteria.
- **Dynamic PDF Resumes:** One-click generation of professional resumes based on platform activity.

## 7. Data Types Used
The project utilizes standard programming data types and NoSQL document structures:
- **Integer:** Used for test scores, question IDs, and analytics counts.
- **Float:** Used for precise calculations, such as percentage scores or aggregate analytics.
- **String:** Used for names, email addresses, hashed passwords, and text content (like question descriptions).
- **Boolean:** Used for flags such as `is_active`, `is_verified`, or `is_admin` (True/False).
- **Array/List:** Used to store lists of items, such as an array of skills `["Python", "React"]` or a list of completed test IDs.
- **Object/Dictionary:** Used to represent complex, nested data structures (JSON documents), which perfectly align with MongoDB's storage format.

## 8. Modules Description
- **Authentication Module:** Handles secure user registration, login, and session management across different user roles.
- **Diagnostic Engine:** Manages the retrieval of test questions, evaluates user answers, and calculates overall performance metrics.
- **Recommendation System:** Analyzes test results to identify knowledge gaps and queries external APIs to fetch curated learning resources.
- **Student Dashboard:** The central hub for learners to view analytics, update profiles, and access learning materials.
- **Recruiter Portal:** The interface for companies to manage job postings and search the platform's talent pool.
- **Admin Control Panel:** Allows system administrators to oversee platform activity, manage users, and update system configurations.

## 9. Working of the Project
1. **Registration:** A user signs up and selects their role (Student, Recruiter, Admin).
2. **Assessment:** A student navigates to the diagnostic section and takes a test tailored to a specific domain (e.g., Frontend Development).
3. **Analysis:** Upon submission, the system calculates the score, logs correct/incorrect answers, and updates the student's skill profile in the database.
4. **Recommendation:** The system identifies exactly where the student failed and fetches relevant tutorial videos to help them improve.
5. **Connection:** A recruiter posts a job requiring specific skills. They use the Talent Discovery tool to search for students whose test scores prove they possess those skills, allowing the recruiter to reach out directly.

## 10. Advantages
- **Objective Verification:** Moves beyond self-reported skills by providing verifiable test results.
- **Targeted Upskilling:** Saves students time by telling them exactly what they need to learn, rather than guessing.
- **Efficient Recruitment:** Drastically reduces the time recruiters spend screening candidates by highlighting proven talent.
- **Scalable & Modern:** Built with a flexible NoSQL database and a modern, responsive user interface.

## 11. Future Scope
- **Third-Party Integrations:** Connecting with platforms like Coursera, Udemy, or LinkedIn for broader credentialing.
- **AI Interview Prep:** Implementing an AI chatbot to conduct mock interviews based on a user's specific skill gaps.
- **Real-time Messaging:** Adding web sockets for direct, real-time communication between recruiters and students.
- **Advanced Predictive Analytics:** Using machine learning to predict career trajectories and suggest optimal learning paths.

## 12. Conclusion
The GapLens Skill Diagnostic Platform is a comprehensive solution designed to modernize the upskilling and recruitment pipeline. By combining dynamic assessments, automated learning recommendations, and direct recruiter access within a premium, user-friendly interface, the project successfully creates an ecosystem where learning is actionable and talent is easily discoverable.
