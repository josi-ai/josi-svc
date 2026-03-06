import { authMiddleware } from '@descope/nextjs-sdk/server';

export default authMiddleware({
  projectId: process.env.NEXT_PUBLIC_DESCOPE_PROJECT_ID || 'P3AXgK6L8OgCfFSKcrNaA99vVChw',
  redirectUrl: '/auth/login',
  publicRoutes: [
    '/',
    '/auth/login',
    '/chart-calculator',
    '/pricing',
    '/api/v1/webhooks/(.*)',
  ],
});

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
