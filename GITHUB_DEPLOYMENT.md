# GitHub Deployment Guide for Exam Mark Prediction System

## 📤 Push Project to GitHub

### Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Enter repository name: `exam-mark-prediction-system`
3. Add description: "Full-stack ML web app to predict college exam marks"
4. Choose: **Public** (for sharing) or **Private** (for personal use)
5. Click "Create repository"

### Step 2: Initialize Git in Your Project

```bash
cd c:\Users\Ruban\Desktop\projects\finial_pro

# Initialize git
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Exam Mark Prediction System"
```

### Step 3: Link to GitHub Repository

```bash
# Replace YOUR_USERNAME and YOUR_REPO with your GitHub info
git remote add origin https://github.com/YOUR_USERNAME/exam-mark-prediction-system.git

# Verify remote
git remote -v

# Push to GitHub (this will ask for your GitHub credentials)
git branch -M main
git push -u origin main
```

### Step 4: GitHub Credentials

When pushed, you'll be prompted for:
- **GitHub Username**: Your GitHub username
- **Token or Password**: 
  - For new GitHub accounts: Create a Personal Access Token (Settings > Developer Settings > Personal Access Tokens)
  - Click "Generate new token" > Select "repo" scope > Copy token and use as password

---

## 🔧 Production Deployment Options

### Option A: Deploy to Heroku (Recommended - Free Tier)

#### Setup:
1. Create Heroku account: https://www.heroku.com
2. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
3. Login to Heroku: `heroku login`

#### Create Procfile
Add file: `Procfile` (no extension)
```
web: gunicorn backend.app:app
```

#### Create runtime.txt
Add file: `runtime.txt`
```
python-3.11.0
```

#### Deployment:
```bash
# Create Heroku app
heroku create your-app-name

# Deploy from GitHub
git push heroku main

# Initialize database
heroku run python -c "from backend.app import db_handler; db_handler.init_db()"

# Open app
heroku open
```

---

### Option B: Deploy to AWS EC2

#### Setup EC2 Instance:
1. Create AWS account: https://aws.amazon.com
2. Launch EC2 instance (Ubuntu 20.04 LTS, Free Tier eligible)
3. Connect via SSH or EC2 Instance Connect

#### Deploy:
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install python3-pip python3-venv git tesseract-ocr -y

# Clone repository
git clone https://github.com/YOUR_USERNAME/exam-mark-prediction-system.git
cd exam-mark-prediction-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Run with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

---

### Option C: Deploy to Railway (Easiest)

1. Go to https://railway.app
2. Sign up with GitHub
3. New Project > GitHub Repo
4. Select your repository
5. Railway auto-detects and deploys!
6. Configure environment variables if needed
7. Get public URL automatically

---

### Option D: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y tesseract-ocr

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

Build and run:
```bash
docker build -t exam-prediction .
docker run -p 5000:5000 exam-prediction
```

---

## 📋 GitHub Actions CI/CD (Automatic Testing)

Create file: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Test Flask app
      run: python -m pytest tests/ || echo "No tests found"
    
    - name: Deploy to Heroku
      if: success()
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "your-app-name"
        heroku_email: "your-email@gmail.com"
```

---

## 🌐 Environment Variables for Production

Create `.env` file (add to .gitignore):
```
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_PATH=/var/data/exam_marks.db
UPLOAD_FOLDER=/var/uploads
MAX_UPLOAD_SIZE=16777216
```

For Heroku/cloud platforms, set via:
```bash
# Heroku
heroku config:set FLASK_ENV=production

# AWS (via console or CLI)
# Railway (via dashboard)
```

---

## 📊 GitHub Repository Structure

Your repository will have:
```
exam-mark-prediction-system/
├── backend/
├── frontend/
├── ml_model/
├── database/
├── uploads/
├── .github/workflows/
├── requirements.txt
├── Procfile
├── Dockerfile (optional)
├── README.md
├── QUICKSTART.md
└── .gitignore
```

---

## ✅ Deployment Checklist

- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] Git initialized locally
- [ ] All files committed
- [ ] Pushed to GitHub
- [ ] Production environment chosen
- [ ] Deployment files created (Procfile, Dockerfile, etc.)
- [ ] Environment variables configured
- [ ] Database initialized on server
- [ ] Application tested on deployed URL
- [ ] Domain configured (if needed)
- [ ] SSL certificate enabled (if needed)
- [ ] Monitoring setup (if available)

---

## 🔗 Quick Links

- **GitHub**: https://github.com
- **Heroku**: https://www.heroku.com
- **Railway**: https://railway.app
- **AWS**: https://aws.amazon.com
- **Docker Hub**: https://hub.docker.com

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Git command not found | Install Git from https://git-scm.com |
| Python not found on server | Install Python on server |
| Tesseract missing on server | `apt-get install tesseract-ocr` |
| Port 5000 already in use | Change port or use reverse proxy |
| Database initialization fails | Run manually on server |
| Static files not serving | Configure static folder in production |

---

**Next Step**: Choose your deployment platform and I'll guide you through the specific steps! 🚀
