# Vercel Deployment Guide for Tekshila

## Pre-deployment Checklist

### 1. Delete Current Vercel Project
- Go to your Vercel dashboard
- Select your Tekshila project
- Settings → Advanced → Delete Project

### 2. GitHub Setup
Create a GitHub OAuth App:
- Go to: https://github.com/settings/applications/new
- Application name: `Tekshila`
- Homepage URL: `https://your-new-vercel-app.vercel.app` (will get this after deployment)
- Authorization callback URL: `https://your-new-vercel-app.vercel.app/api/auth-github`
- Save the **Client ID** (you'll need this)

### 3. Deploy to Vercel
1. Go to vercel.com and click "New Project"
2. Import your GitHub repository
3. **Import settings:**
   - Framework Preset: `Other`
   - Root Directory: `./` (leave default)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: (leave empty)

### 4. Set Environment Variables
After deployment, go to:
- Project Settings → Environment Variables
- Add: `GITHUB_CLIENT_ID` = `your_github_oauth_client_id_from_step_2`
- Apply to: Production, Preview, Development

### 5. Update GitHub OAuth App
- Go back to your GitHub OAuth App settings
- Update the URLs with your actual Vercel domain:
  - Homepage URL: `https://your-actual-vercel-app.vercel.app`
  - Authorization callback URL: `https://your-actual-vercel-app.vercel.app/api/auth-github`

### 6. Test Deployment
After deployment, test these URLs:
- `https://your-app.vercel.app/` (should show your main page)
- `https://your-app.vercel.app/api/test` (should return JSON)
- `https://your-app.vercel.app/api/config` (should return config with your client ID)

## Troubleshooting
If you get errors:
1. Check Vercel Function Logs in the dashboard
2. Verify environment variables are set
3. Check GitHub OAuth app URLs match your domain

## Files included in deployment:
- `frontend/` directory (HTML, CSS, JS files)
- `api/` directory (Python serverless functions)
- `vercel.json` (routing configuration)
- `.vercelignore` (deployment exclusions)
