import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const LEGACY_PATHS: Record<string, string> = {
  "/legacy-audit": "/",
  "/old-reviews": "/",
  "/v1": "/",
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (LEGACY_PATHS[pathname]) {
    const destination = new URL(LEGACY_PATHS[pathname], request.url);
    // Explicit 301 Moved Permanently status code (Requirement 10)
    return NextResponse.redirect(destination, 301);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/legacy-audit", "/old-reviews", "/v1"],
};
