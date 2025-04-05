'use client';

import { useUser } from '@auth0/nextjs-auth0/client';
import React from 'react';
import LoginButton from './LoginButton';
import LogoutButton from './LogoutButton';

export default function Profile() {
  const { user, error, isLoading } = useUser();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="p-4">
      {user ? (
        <div className="flex flex-col items-center gap-4">
          {user.picture && (
            <img 
              src={user.picture} 
              alt={user.name || 'User'} 
              className="rounded-full w-16 h-16"
            />
          )}
          <h2 className="text-xl font-bold">{user.name}</h2>
          <p>{user.email}</p>
          <LogoutButton />
        </div>
      ) : (
        <LoginButton />
      )}
    </div>
  );
} 