import { handleAuth } from '@auth0/nextjs-auth0';

// Following Auth0's recommended approach for App Router
// The warning about params.auth0 is a known issue but doesn't affect functionality
// See: https://github.com/auth0/nextjs-auth0/issues/1304
export const GET = handleAuth();
export const POST = handleAuth();