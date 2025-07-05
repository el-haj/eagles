# Getting Started with Security Eagles Project

Welcome! This guide will help you set up and run the Security Eagles project on your local machine.

## Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- (Optional) Virtual environment tool: `venv` or `virtualenv`
- Git (to clone the repository, if needed)

## Backend Setup

1. **Navigate to the Backend Directory**
   ```sh
   cd Backend/security-eagles
   ```

2. **Create and Activate a Virtual Environment (Recommended)**
   - On Windows:
     ```sh
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Apply Database Migrations**
   ```sh
   python manage.py migrate
   ```

5. **Create a Superuser (Admin Account)**
   ```sh
   python manage.py createsuperuser
   ```
   Follow the prompts to set up your admin credentials.

6. **Run the Development Server**
   ```sh
   python manage.py runserver
   ```
   The server will start at `http://127.0.0.1:8000/` by default.

7. **Access the Admin Panel**
   Go to `http://127.0.0.1:8000/admin/` and log in with the superuser credentials.

## Frontend & SSO
- The Frontend and SSO folders are present but not configured in this guide. Please refer to their respective documentation or contact the project maintainer for setup instructions.

## Running Tests
To run backend tests:
```sh
python manage.py test
```

## Troubleshooting
- If you encounter issues with dependencies, ensure your virtual environment is activated.
- For database issues, try deleting `db.sqlite3` and rerunning migrations.

## Need Help?
Contact the project maintainer or check the README.md for more details.

---
