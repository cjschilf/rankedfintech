import { NextRequest, NextResponse } from 'next/server';
import { getSession } from '@auth0/nextjs-auth0';
import { createOrUpdateUser } from '../../../../lib/users';

export async function POST(req: NextRequest) {
  try {
    // Get the current user from client-side passed information
    // Since we can't reliably use getSession() in App Router API routes
    const body = await req.json().catch(() => ({}));
    
    // If client didn't send user info, return unauthorized
    if (!body.user) {
      return NextResponse.json(
        { error: 'User information not provided' },
        { status: 401 }
      );
    }
    
    const { user } = body;

    if (!user || !user.sub || !user.email) {
      return NextResponse.json(
        { error: 'Invalid user information' },
        { status: 401 }
      );
    }

    // Extract user data from client-sent user object
    const userData = {
      auth0Id: user.sub,
      email: user.email,
      name: user.name,
      picture: user.picture
    };

    // Save to MongoDB (ELO will be set to 1000 for new users)
    const savedUser = await createOrUpdateUser(userData);

    return NextResponse.json({ success: true, user: savedUser });
  } catch (error) {
    console.error('Error saving user profile:', error);
    return NextResponse.json(
      { error: 'Failed to save user profile' },
      { status: 500 }
    );
  }
} 