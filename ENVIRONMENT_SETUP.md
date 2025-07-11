# Environment Configuration Guide

## Required Environment Variables

To fix the "Configuration not loaded" error, you need to set up the following environment variables in your Vercel deployment:

### 1. GitHub OAuth Application Setup

First, create a GitHub OAuth App:

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - Application name: `Tekshila`
   - Homepage URL: `https://your-vercel-domain.vercel.app`
   - Authorization callback URL: `https://your-vercel-domain.vercel.app/api/auth/github/callback`
4. Click "Register application"
5. Copy the **Client ID** and generate a **Client Secret**

### 2. Vercel Environment Variables

In your Vercel dashboard, go to your project settings and add these environment variables:

```bash
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
```

### 3. Local Development Setup

For local development, create a `.env` file in your project root:

```bash
# .env (for local development)
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
VERCEL_URL=http://localhost:3000
```

### 4. Verification Steps

After setting up the environment variables:

1. **Deploy the latest changes** to Vercel
2. **Check the health endpoint**: Visit `https://your-domain.vercel.app/api/health`
3. **Check the config endpoint**: Visit `https://your-domain.vercel.app/api/config`
4. **Test the login**: Visit your application and try to log in

### 5. Troubleshooting

If you're still getting errors:

1. **Check Vercel Function Logs**:
   - Go to Vercel Dashboard → Your Project → Functions
   - Check the logs for any errors

2. **Verify OAuth App Settings**:
   - Ensure the callback URL matches exactly
   - Check that the Client ID and Secret are correct

3. **Test API Endpoints**:
   - `/api/health` - Should return server status
   - `/api/config` - Should return configuration (without secrets)

4. **Browser Network Tab**:
   - Open DevTools → Network tab
   - Look for failed requests to `/api/config`
   - Check the response for error details

### 6. Quick Fix Commands

If you need to redeploy quickly:

```bash
# Force redeploy (create empty file to trigger deployment)
echo "$(date)" > deployment-trigger.txt
git add deployment-trigger.txt
git commit -m "Force redeploy to apply environment variables"
git push
```

## Security Notes

- Never commit actual environment variables to your repository
- Use different OAuth apps for development and production
- Regularly rotate your GitHub Client Secret
- Monitor your OAuth app's usage in GitHub settings

## Support

If you continue to experience issues:

1. Check the browser console for detailed error messages
2. Review Vercel function logs
3. Verify all environment variables are set correctly
4. Ensure your GitHub OAuth app configuration matches your domain
