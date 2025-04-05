'use client';

import React from 'react';

export default function LoginButton() {
  return (
    <a 
      href="/api/auth/login"
      className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    >
      Log In
    </a>
  );
} 