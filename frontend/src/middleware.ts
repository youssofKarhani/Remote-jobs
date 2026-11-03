import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const sitePassword = process.env.SITE_PASSWORD;

  // If SITE_PASSWORD is not configured, site remains open to the public
  if (!sitePassword) {
    return NextResponse.next();
  }

  const { pathname } = req.nextUrl;

  // Allow static files, favicon, and Next.js internal bundles
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/static') ||
    pathname === '/favicon.ico' ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // 1. One-click unlock via query param: e.g. https://findjobfit.de/?pass=<PASSWORD>
  const queryPass = req.nextUrl.searchParams.get('pass');
  if (queryPass && queryPass === sitePassword) {
    const cleanUrl = req.nextUrl.clone();
    cleanUrl.searchParams.delete('pass');
    const response = NextResponse.redirect(cleanUrl);
    response.cookies.set('site_access', sitePassword, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 24 * 30, // 30 days
    });
    return response;
  }

  // 2. Cookie authentication: user has already logged in previously
  const accessCookie = req.cookies.get('site_access')?.value;
  if (accessCookie && accessCookie === sitePassword) {
    return NextResponse.next();
  }

  // 3. HTTP Basic Authentication header check
  const authHeader = req.headers.get('authorization');
  if (authHeader && authHeader.startsWith('Basic ')) {
    try {
      const base64Credentials = authHeader.split(' ')[1];
      const credentials = atob(base64Credentials);
      const separatorIndex = credentials.indexOf(':');
      const password = separatorIndex !== -1 ? credentials.substring(separatorIndex + 1) : credentials;

      if (password === sitePassword) {
        const response = NextResponse.next();
        response.cookies.set('site_access', sitePassword, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          path: '/',
          maxAge: 60 * 60 * 24 * 30,
        });
        return response;
      }
    } catch {
      // Invalid base64 encoding; fall through to 401 prompt
    }
  }

  // Request HTTP Basic Auth
  return new NextResponse('Authentication Required. Please enter the site password to access the platform.', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Protected RemoteJobs Platform"',
    },
  });
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
