# Deployment Checklist

## Pre-Deployment Setup

### 1. GitHub OAuth App Configuration
- [ ] Created GitHub OAuth App
- [ ] Set Homepage URL: `https://your-domain.vercel.app`
- [ ] Set Authorization callback URL: `https://your-domain.vercel.app/api/auth/github/callback`
- [ ] Copied Client ID
- [ ] Generated and copied Client Secret

### 2. Vercel Environment Variables
- [ ] `GITHUB_CLIENT_ID` set in Vercel dashboard
- [ ] `GITHUB_CLIENT_SECRET` set in Vercel dashboard
- [ ] Environment variables applied to production environment

### 3. Code Deployment
- [ ] Latest code committed to main branch
- [ ] `vercel.json` properly configured with `rewrites` (not `routes`)
- [ ] All API endpoints exist and are functional
- [ ] Frontend properly references API endpoints

## Post-Deployment Verification

### 1. API Health Checks
- [ ] `/api/health` returns 200 with environment status
- [ ] `/api/config` returns 200 with GitHub client ID
- [ ] No missing environment variables in config response

### 2. Frontend Functionality
- [ ] Main page loads without errors
- [ ] Login page loads and shows "Continue with GitHub" button
- [ ] No "Configuration not loaded" errors
- [ ] GitHub OAuth flow works end-to-end

### 3. Browser Console
- [ ] No JavaScript errors in console
- [ ] API requests return successful responses
- [ ] Network tab shows 200 responses for `/api/config`

## Quick Tests

### Manual Testing
1. **Visit login page**: Should show enabled GitHub login button
2. **Click GitHub login**: Should redirect to GitHub OAuth
3. **Complete OAuth**: Should redirect back and show main dashboard
4. **Check user display**: Avatar and username should appear

### Automated Testing
```bash
# Run diagnostic script
./diagnose.sh

# Test specific endpoints
curl https://your-domain.vercel.app/api/health
curl https://your-domain.vercel.app/api/config
```

## Emergency Fixes

### If "Configuration not loaded" persists:

1. **Check Vercel Function Logs**:
   - Go to Vercel Dashboard → Functions
   - Look for errors in recent invocations

2. **Redeploy with Environment Variables**:
   ```bash
   # Force redeploy
   git commit --allow-empty -m "Force redeploy"
   git push
   ```

3. **Verify OAuth App**:
   - Double-check GitHub OAuth app settings
   - Ensure Client ID/Secret match exactly

4. **Test API Directly**:
   ```bash
   # Should return configuration
   curl -v https://your-domain.vercel.app/api/config
   ```

## Rollback Plan

If deployment fails:
1. Revert to previous working commit
2. Push to trigger rollback deployment
3. Verify environment variables are still set
4. Test basic functionality

## Success Criteria

✅ **Deployment is successful when**:
- Login page loads with enabled GitHub button
- OAuth flow completes successfully  
- Main dashboard shows user information
- All API endpoints respond correctly
- No console errors or configuration warnings
