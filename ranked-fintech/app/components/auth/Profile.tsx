'use client';

import { useUser } from '@auth0/nextjs-auth0/client';
import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import LoginButton from './LoginButton';
import LogoutButton from './LogoutButton';

// Define a type for our MongoDB user which includes the ELO field
interface MongoDBUser {
  _id: string;
  auth0Id: string;
  name?: string;
  email: string;
  picture?: string;
  elo: number;
  createdAt: string;
  updatedAt: string;
  lastLogin: string;
}

export default function Profile() {
  const { user, error, isLoading } = useUser();
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [mongoUser, setMongoUser] = useState<MongoDBUser | null>(null);

  useEffect(() => {
    // If user is logged in, save their profile to MongoDB
    const saveUserProfile = async () => {
      if (user && !isSaving) {
        try {
          setIsSaving(true);
          setSaveError(null);
          
          // Now we send the user data to the API
          const response = await fetch('/api/user/save-profile', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user })
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to save profile');
          }
          
          // Profile saved successfully
          const data = await response.json();
          setMongoUser(data.user);
          console.log('Profile saved to MongoDB');
        } catch (err) {
          console.error('Error saving profile:', err);
          setSaveError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
          setIsSaving(false);
        }
      }
    };

    saveUserProfile();
  }, [user, isSaving]);

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
          
          {/* Display ELO rating - read-only */}
          {mongoUser && (
            <div className="bg-blue-100 dark:bg-blue-900 p-2 rounded-md text-center">
              <p className="text-sm font-medium">ELO Rating</p>
              <p className="text-xl font-bold">{mongoUser.elo}</p>
            </div>
          )}
          
          {saveError && (
            <p className="text-red-500 text-sm">{saveError}</p>
          )}
          <LogoutButton />
        </div>
      ) : (
        <LoginButton />
      )}
    </div>
  );
} 