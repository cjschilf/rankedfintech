'use client';

import React from 'react';
import Link from 'next/link';

export default function LoginButton() {
  return (
    <Link 
      href="/api/auth/login"
      className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded inline-block"
    >
      Log In
    </Link>
  );
} 