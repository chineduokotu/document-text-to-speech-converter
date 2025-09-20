# Deployment Guide - Railway & Render

## Prerequisites
1. GitHub account
2. Railway account (https://railway.app) OR Render account (https://render.com)

## Files Created for Deployment
- `Procfile` - Tells Railway how to run the app
- `runtime.txt` - Specifies Python version for Railway
- `render.yaml` - Configuration for Render deployment
- `pyproject.toml` - Python project metadata
- `setup.py` - Python package setup
- `start.py` - Simple start script for Render
- `Dockerfile` - Docker configuration as backup
- `.gitignore` - Excludes unnecessary files
- Updated `requirements.txt` - Clean dependencies list
- Modified `run_webapp.py` - Uses PORT environment variable
- Renamed `main.py` to `cli_main.py` - Avoids deployment confusion

## Option 1: Deploy to Railway

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Deploy to Railway
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Python and deploy

### 3. Get Your URL
After deployment, Railway will provide a URL like:
`https://your-app-name.up.railway.app`

## Option 2: Deploy to Render

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy to Render
1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` configuration
5. Click "Create Web Service"

### 3. Get Your URL
After deployment, Render will provide a URL like:
`https://your-app-name.onrender.com`

## Environment Variables (Optional)
You can add these in your deployment platform dashboard:
- `SECRET_KEY` - For Flask sessions (generate a random string)
- `FLASK_ENV` - Set to "production"

## Troubleshooting

### "Could not find Cargo.toml" error on Render:
This means Render detected your project as Rust instead of Python. The `render.yaml` and `pyproject.toml` files I created should fix this.

### If deployment still fails:
1. Check build logs in your deployment platform
2. Ensure all dependencies are in requirements.txt
3. Verify Python version compatibility
4. Try redeploying after the files are committed

### If TTS doesn't work:
The app now includes Google Cloud Text-to-Speech integration. To enable TTS:

#### Quick Setup (Free):
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Cloud Text-to-Speech API"
4. Create a service account with "Cloud Text-to-Speech User" role
5. Download JSON credentials
6. Upload `google-credentials.json` to your `src/` folder
7. Redeploy your app

#### Free Tier Limits:
- **Google Cloud TTS**: 1 million characters/month free
- **No credit card required** for free tier

#### Without Google Cloud:
The app will still work for document processing, just without TTS functionality.

### For mobile access:
- Use the deployment URL on your mobile browser
- Works on any device with internet connection

## Cost Comparison
- **Railway**: Generous free tier, paid plans from $5/month
- **Render**: Free tier (750 hours/month), paid plans from $7/month

Both platforms offer free tiers sufficient for testing and light usage.