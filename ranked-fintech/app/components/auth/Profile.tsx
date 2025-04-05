'use client';

import { useUser } from '@auth0/nextjs-auth0/client';
import React from 'react';
import Image from 'next/image';
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
            <div className="relative w-16 h-16 rounded-full overflow-hidden">
              <Image 
                src={user.picture} 
                alt={user.name || 'User'} 
                fill
                sizes="(max-width: 768px) 100vw, 64px"
                style={{ objectFit: 'cover' }}
                priority
              />
            </div>
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