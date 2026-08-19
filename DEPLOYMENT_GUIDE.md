# Deploying SafeSignal — Railway (backend) + Vercel (frontend)

## PART A — Backend on Railway

### 1. Prep files locally first
Replace these files with the new production versions I gave you:
- `settings_prod.py` → `safesignal/settings.py` (overwrite)
- `requirements_prod.txt` → `requirements.txt` (overwrite)
- `Procfile` → project root (new file, no extension)

Then commit and push to GitHub:
```powershell
git add .
git commit -m "Production-ready settings for deployment"
git push
```

### 2. Create Railway account + project
1. Go to https://railway.app → Sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `safesignal` repo
4. Railway will detect it's a Python project

### 3. Add Redis
1. In your Railway project, click **"+ New"** → **"Database"** → **"Add Redis"**
2. Railway auto-creates a `REDIS_URL` variable and links it to your service

### 4. Add PostgreSQL (optional but recommended over SQLite for a real deployed app)
1. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway auto-creates `DATABASE_URL`

### 5. Set environment variables
In your web service → **"Variables"** tab, add:
```
SECRET_KEY=<generate a random 50-char string>
DEBUG=False
ALLOWED_HOSTS=*.railway.app
ANTHROPIC_API_KEY=<your new key>
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-frontend.vercel.app
```
(`REDIS_URL` and `DATABASE_URL` are already set automatically by Railway.)

### 6. Set the start command
In your web service → **"Settings"** → **"Deploy"** → Start Command:
```
daphne -b 0.0.0.0 -p $PORT safesignal.asgi:application
```

### 7. Add a second service for Celery worker
1. **"+ New"** → **"GitHub Repo"** → same repo again
2. This service's Start Command:
```
celery -A safesignal worker -l info
```
3. Give it the same environment variables as the web service (copy them over)

### 8. Run migrations
Railway gives you a shell — in your web service, click **"..."** → **"Shell"**, then:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 9. Get your public URL
Railway → your web service → **"Settings"** → **"Networking"** → **"Generate Domain"**
You'll get something like `https://safesignal-production.up.railway.app`

---

## PART B — Frontend on Vercel

### 1. Update the API base URL
In `frontend/src/api/client.js`, change:
```js
const API_BASE = "http://127.0.0.1:8000/api";
```
to:
```js
const API_BASE = "https://safesignal-production.up.railway.app/api";
```
(use your actual Railway URL)

Commit and push this change.

### 2. Deploy on Vercel
1. Go to https://vercel.com → Sign up with GitHub
2. **"Add New"** → **"Project"** → import your `safesignal` repo
3. **Root Directory**: set to `frontend`
4. **Framework Preset**: Vite (auto-detected)
5. Click **"Deploy"**

Vercel gives you a URL like `https://safesignal.vercel.app` — this is your **public app link** to share for user testing and Product Hunt.

### 3. Update backend CORS
Go back to Railway → your web service → Variables → update:
```
CORS_ALLOWED_ORIGINS=https://safesignal.vercel.app
CSRF_TRUSTED_ORIGINS=https://safesignal.vercel.app
```
Redeploy (Railway auto-redeploys on variable change).

---

## Quick checklist
- [ ] Railway backend deployed, public URL working
- [ ] Redis + Postgres attached
- [ ] Celery worker service running
- [ ] Migrations run, superuser created
- [ ] Vercel frontend deployed, pointing to Railway backend URL
- [ ] CORS updated to allow the Vercel domain
- [ ] Test: register, login, raise SOS from the live public URL

Once this works, `https://safesignal.vercel.app` is your shareable link — for judges, for your 50 users, and for Product Hunt.
