# Kanvas Backend Server API

A Django 5 + Django REST Framework API backing Kanvas, serving as the secure data vault for task lists and image annotations.

---

## 🛠️ Tech Stack & Requirements
*   **Python:** 3.13.5 (configured inside Virtual Environment)
*   **Framework:** Django 5+ & Django REST Framework
*   **Database:** SQLite in development, utilizing WAL (Write-Ahead Logging) mode.
*   **Image Processing:** Pillow for image measurements and scaling fallbacks.
*   **External Integrations:** ImgBB API for image cloud uploads.

---

## 🚀 Setup & Execution

### 1. Initialize Virtual Environment & Install Dependencies
From the `Kanvas-Server/` directory:
```bash
# Create the virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install django djangorestframework pillow requests bcrypt django-cors-headers
```

### 2. Configure Environment Variables
Create a `.env` file or export variables in your shell (our Django app reads `IMGBB_API_KEY` from the system environment):
```env
# Optional: Set your ImgBB API key. If not provided, it will fallback to local storage.
IMGBB_API_KEY=your_imgbb_api_key_here
```

### 3. Generate Database Migrations & Migrate
```bash
python manage.py makemigrations users tasks annotations
python manage.py migrate
```

### 4. Seed the Demo User
Initialize the Better Auth compatible database user credentials (`demo@example.com` / `password123`):
```bash
python manage.py seed_user
```

### 5. Run the Server
```bash
python manage.py runserver 8000
```
The Django API will be accessible on `http://localhost:8000`.

---

## 💾 Production Swap: SQLite to PostgreSQL
To upgrade this API to PostgreSQL for a production launch:

1.  **Install pg driver:**
    `pip install psycopg2-binary`
2.  **Update settings.py database engine:**
    Replace the `DATABASES` entry in `core/settings.py` with:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'kanvas_db',
            'USER': 'postgres',
            'PASSWORD': 'your_db_password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```
3.  **Run migrations:**
    Run `python manage.py migrate` to apply the migrations. (Ensure Next.js Better Auth is also pointed to PostgreSQL using its postgres database adapter).

---

## 🧠 Challenges & Solutions

### 1. DB Concurrency Lock (SQLite WAL Mode)
**Challenge:** Sharing a single SQLite file between the Next.js process (writing auth states) and the Django process (writing tasks) can result in `database is locked` concurrency errors.
**Solution:** We configured SQLite inside Django's database connection hooks to run in **Write-Ahead Logging (WAL)** mode:
```python
'init_command': 'PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;'
```
WAL permits concurrent readers and prevents database locking during dual writes, ensuring the Next.js auth server and Django API communicate seamlessly.

### 2. Cross-Language Session Sharing (Better Auth)
**Challenge:** Next.js uses Better Auth (a Node library) while the API runs in Python. Passing JWTs across servers adds network latency.
**Solution:** Since both processes share the SQLite database, Django queries the `session` table directly to verify active user sessions based on the cookie session token, avoiding HTTP hops.
