# Status Check - Task Tracker MVP

A modern, fast, and responsive Task Tracker (Commitments) dashboard built as an MVP. This project features a RESTful API, token-based authentication, and a dynamic drag-and-drop calendar interface with a dark mode toggle.

## 🚀 Tech Stack
* **Backend:** FastAPI, Python 3, SQLAlchemy (ORM)
* **Database:** SQLite (using naive datetimes to prevent timezone shifting)
* **Security:** OAuth2 Token-based Authentication
* **Frontend:** Vanilla JavaScript, Bootstrap 5 (Bootswatch Darkly/Flatly), FullCalendar.js, SweetAlert2

## ✨ Key Features
* **Interactive Calendar:** Drag and drop tasks to change deadlines seamlessly.
* **Smart Statuses:** Tasks automatically display as "Expired" if the deadline passes.
* **Authentication:** Fully protected API endpoints.
* **Dynamic Dashboard:** Real-time stats and inline filtering (by Project or Reviewer).
* **AI Pair Programming:** This MVP was actively developed using AI agents for rapid prototyping, logic structuring, and UI/UX polishing.

## 🛠️ How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt

Run the FastAPI server:

Bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
Open http://127.0.0.1:8000/ in your browser.

Default Login:

Username: admin

Password: password123