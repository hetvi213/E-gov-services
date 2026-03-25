# E-Gov Application - Render Deployment Guide

## Pre-Deployment Checklist ✅

1. **Security Issues Fixed**
   - [x] Moved all credentials to environment variables
   - [x] Created `.env.example` template
   - [x] Created `.gitignore` to prevent `.env` commits

2. **Code Ready**
   - [x] `wsgi.py` created for production server
   - [x] `render.yaml` configuration added
   - [x] `requirements.txt` updated with gunicorn

## Step 1: Prepare Your Repository

```bash
# Navigate to your project
cd "c:\Users\Hetvi\OneDrive\Desktop\E-Gov"

# Initialize git (if not already done)
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Secure credentials with environment variables"

# Push to GitHub
git push origin main
```

## Step 2: Create Render Account & Deploy

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: e-gov (or any name)
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: Free (or Starter)

## Step 3: Add Environment Variables in Render

In the Render dashboard, go to **Environment** and add:

```
FLASK_SECRET=your-production-secret-key
DATABASE_URL=mysql+mysqlconnector://user:password@host:3306/gov_services
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-gmail-password
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE=+1234567890
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_SECRET=your-razorpay-secret
DB_HOST=your-mysql-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=gov_services
```

## Step 4: Configure Database

### Option A: Use External MySQL (Recommended)
- Create MySQL database on services like:
  - [ClearDB](https://www.cleardb.com/) (free tier)
  - [AWS RDS](https://aws.amazon.com/rds/)
  - [DigitalOcean Managed Database](https://www.digitalocean.com/products/managed-databases-mysql/)
  
- Update `DATABASE_URL` and related env vars with your MySQL connection details

### Option B: Keep Local MySQL (Not Recommended for Production)
- Ensure your local MySQL is accessible from Render (requires port forwarding/tunneling)

## Step 5: Handle File Uploads

Render provides ephemeral storage that disappears when the app redeploys. For persistent uploads:

### Option A: Use AWS S3 (Recommended)
```python
# Install: pip install boto3
import boto3
s3 = boto3.client('s3')
# Upload files to S3 instead of local folder
```

### Option B: Use Render Disk
- Create a disk in Render (as configured in `render.yaml`)
- Mount at `/opt/render/project/src/uploads`

## Step 6: Deploy

1. Push your code to GitHub
2. Render automatically deploys (you'll see build logs)
3. Once deployed, visit your app URL: `https://your-app-name.onrender.com`

## Important Notes

### ⚠️ Render Free Tier Limitations
- Apps spin down after 15 minutes of inactivity
- 0.5GB RAM
- Limited to 100MB disk storage
- Slower performance

### ✅ Recommended for Production
Upgrade to Starter Plan ($7/month) or higher for:
- Always-on servers
- More resources
- Better performance
- Production-grade SLA

## Troubleshooting

### Deployment Fails
1. Check Build Logs in Render dashboard
2. Ensure all required packages in `requirements.txt`
3. Check for syntax errors: `python -m py_compile app.py`

### Database Connection Error
1. Verify `DATABASE_URL` is correct
2. Check database credentials in environment variables
3. Ensure database is accessible from Render (firewall rules)

### App crashes after deployment
1. Check Live Logs in Render dashboard
2. Verify all environment variables are set
3. Test locally: `python app.py`

### Email/SMS not sending
1. Verify credentials in environment variables
2. Check Gmail: Generate App Password (not regular password)
3. Verify Twilio credentials are correct

## Local Testing Before Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
# Copy .env.example to .env and fill in values

# Run with gunicorn (same as production)
gunicorn wsgi:app

# Or run with Flask dev server
python app.py
```

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Create Render account
3. ✅ Connect repository and deploy
4. ✅ Add environment variables
5. ✅ Test application
6. ✅ Monitor logs for errors
7. ✅ Set up email/SMS providers

## Support

- Render Docs: https://render.com/docs
- Flask Docs: https://flask.palletsprojects.com/
- Python Deployment: https://www.python.org/dev/peps/pep-0008/

---

**Questions?** Check Render's live logs or test locally first.
