# Esthetician Appointment Scheduler

A Django web application for managing esthetician appointments.  
Users can register, log in, and create, view, edit, or delete appointments.

## Local Setup and Installation

1. Clone the repository and move into it:

```bash
git clone <https://github.com/Shen711/SDEV-265-Appmt_Scheduler-Project.git>
cd SDEV-265-Appmt_Scheduler-Project
```

2. Create and activate a virtual environment:

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start the local server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.
