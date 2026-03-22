import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isPublicRoute = createRouteMatcher([
  '/',
  '/auth/login(.*)',
  '/auth/sign-up(.*)',
  '/chart-calculator',
  '/chart-preview',
  '/pricing',
  '/api/v1/webhooks/(.*)',
  '/constellations/(.*)',
]);

export const proxy = clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
