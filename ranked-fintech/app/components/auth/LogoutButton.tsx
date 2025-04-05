'use client';

import React from 'react';

export default function LogoutButton() {
  return (
    <a 
      href="/api/auth/logout"
      className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
    >
      Log Out
    </a>
  );
} 