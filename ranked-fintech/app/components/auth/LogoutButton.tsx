'use client';

import React from 'react';
import Link from 'next/link';

export default function LogoutButton() {
  return (
    <Link 
      href="/api/auth/logout"
      className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded inline-block"
    >
      Log Out
    </Link>
  );
} 