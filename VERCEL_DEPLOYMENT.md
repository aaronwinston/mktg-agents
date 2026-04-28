# ForgeOS Vercel Deployment Guide

## Overview

Vercel provides the easiest way to deploy the ForgeOS frontend (Next.js) with automatic scaling, CDN, and serverless functions. This guide walks through deploying to Vercel.

## Prerequisites

- Vercel account (https://vercel.com)
- GitHub account with admin access to your repo
- Vercel CLI installed (`npm i -g vercel`)

## Deployment Options

### Option 1: GitHub Integration (Recommended)

**Automatic deployment on every push to main branch.**

1. **Connect GitHub to Vercel:**
   ```bash
   vercel link
   # or visit https://vercel.com/new and import your GitHub repo
   ```

2. **Configure Project:**
   - Select `aaronwinston/forgeos` repository
   - Framework: Next.js (auto-detected)
   - Root Directory: `./apps/web`
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

3. **Set Environment Variables:**
   ```bash
   vercel env add NEXT_PUBLIC_API_BASE_URL
   # Enter: https://your-api-domain.com (for production)
   # Choose: Production environment
   
   vercel env add NEXT_PUBLIC_API_BASE_URL
   # Enter: http://localhost:8000 (for preview)
   # Choose: Preview environment
   ```

4. **Deploy:**
   ```bash
   # This happens automatically on push to main
   git push origin main
   # Vercel will auto-deploy within 1-2 minutes
   ```

### Option 2: Manual Deployment via CLI

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Deploy Frontend:**
   ```bash
   cd /Users/aaronwinston/forgeos
   vercel deploy --prod
   ```

3. **Set Environment Variables:**
   ```bash
   vercel env add NEXT_PUBLIC_API_BASE_URL production
   ```

## Configuration

### vercel.json

The `vercel.json` file at the repo root configures:
- Build and output directories
- Environment variables
- Security headers (CSP, X-Frame-Options, etc.)
- Redirects and rewrites
- API endpoint proxying

### Security Headers

CSP and other security headers are configured in `vercel.json` and applied to all routes:
- Content-Security-Policy
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection
- Referrer-Policy

### API Proxying

Frontend API calls are proxied to the backend:
```
/api/* -> http://localhost:8000/api/*
```

For production, update this to your backend domain:
```json
"rewrites": [
  {
    "source": "/api/:path*",
    "destination": "https://api.yourdomain.com/api/:path*"
  }
]
```

## Environment Variables

### For Vercel

Set in Vercel dashboard under **Settings > Environment Variables**:

**Production:**
```
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
```

**Preview (branches):**
```
NEXT_PUBLIC_API_BASE_URL=https://staging-api.yourdomain.com
```

**Development:**
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Local Development

Create `.env.local` in `apps/web/`:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Deployment Flow

### Automatic (GitHub Integration)

1. Push to main branch
2. GitHub notifies Vercel
3. Vercel builds and deploys
4. Get deployment URL in PR/commit status
5. Preview available at `forgeOS-<hash>.vercel.app`

### Domains

- **Production:** `yourdomain.com` or `app.yourdomain.com`
- **Preview:** `forgeOS-<branch>.vercel.app`
- **Staging:** `staging.yourdomain.com`

## Monitoring & Analytics

### Vercel Dashboard

Access at https://vercel.com/dashboard

Monitor:
- Deployment status and history
- Performance metrics
- Errors and exceptions
- Build logs
- Analytics and traffic

### Real User Monitoring (RUM)

Enable in Vercel project settings to track:
- Page load times
- Core Web Vitals
- User interactions
- Error rates

## Optimization

### Image Optimization

Vercel auto-optimizes images via Next.js Image component.

### Caching

Set in `vercel.json`:
```json
"headers": [
  {
    "source": "/(.*)",
    "headers": [
      {
        "key": "Cache-Control",
        "value": "public, max-age=3600, s-maxage=3600"
      }
    ]
  }
]
```

### Code Splitting

Next.js automatically code-splits at page boundaries. Use dynamic imports for large components:

```typescript
import dynamic from 'next/dynamic';
const HeavyComponent = dynamic(() => import('./Heavy'));
```

## Troubleshooting

### Build Fails

Check build logs in Vercel dashboard:
1. Go to Deployments
2. Click on failed deployment
3. View detailed build logs
4. Common issues:
   - Missing environment variables
   - TypeScript errors
   - Node.js version mismatch

### API Calls Fail

Verify:
1. `NEXT_PUBLIC_API_BASE_URL` is set correctly
2. Backend API is running and accessible
3. CORS is configured on backend
4. Check network tab in DevTools

### Performance Issues

1. Check Lighthouse score in Vercel Analytics
2. Reduce bundle size (code splitting, dynamic imports)
3. Optimize images (use Next.js Image component)
4. Enable ISR (Incremental Static Regeneration) if applicable

## Production Checklist

- [ ] Domain configured in Vercel
- [ ] SSL certificate installed (auto via Vercel)
- [ ] Environment variables set for production
- [ ] Backend API running and accessible
- [ ] Sentry DSN configured
- [ ] Analytics enabled
- [ ] Error tracking enabled
- [ ] Monitoring alerts configured
- [ ] CDN cache configured
- [ ] Security headers validated

## Rollback

If deployment has issues:

1. **Via Vercel Dashboard:**
   - Go to Deployments
   - Find previous working deployment
   - Click three dots → Promote to Production

2. **Via CLI:**
   ```bash
   vercel deployments --limit 20
   vercel promote <deployment-url>
   ```

## Cost Optimization

Vercel pricing:
- **Pro Plan:** $20/month
  - Unlimited projects
  - Unlimited builds
  - Priority support
- **Enterprise:** Custom pricing for high volume

Cost drivers:
- Build minutes (free 6000/month on Pro)
- Edge middleware invocations
- Serverless Function execution time
- Bandwidth

Reduce costs by:
- Caching aggressively
- Using Edge Functions for static content
- Optimizing bundle size
- Using ISR for static generation

## CI/CD Integration

Vercel integrates with:
- GitHub (native)
- GitLab (via OAuth)
- Bitbucket (via OAuth)
- Gitea (via OAuth)

For each deployment:
1. Vercel runs build command
2. Runs tests (if configured in `package.json`)
3. Generates preview URL
4. Deploys to production on merge to main

## Serverless Functions

ForgeOS doesn't use serverless functions on Vercel (API runs separately), but you can add edge functions for:
- Request authentication
- Rate limiting
- Custom routing
- A/B testing

See: https://vercel.com/docs/edge-functions/overview

## Further Reading

- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)

---

**Last Updated:** 2026-04-27  
**Status:** ✅ Ready for Vercel Deployment
