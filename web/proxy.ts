import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

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

const isAuthRoute = createRouteMatcher([
  '/auth/login(.*)',
  '/auth/sign-up(.*)',
]);

export const proxy = clerkMiddleware(async (auth, request) => {
  const { userId } = await auth();

  if (isAuthRoute(request)) {
    // Valid session — no need to show login, send them to dashboard
    if (userId) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
    // No valid session — clear any stale Clerk cookies so <SignIn> gets a clean slate
    const response = NextResponse.next();
    response.cookies.delete('__session');
    response.cookies.delete('__client_uat');
    return response;
  }

  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
