# Ranked Fintech

A Next.js application for financial ranking and analysis with Auth0 authentication integration.

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Auth0 account

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ranked-fintech
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure Auth0:
   - Create an Auth0 application at [https://manage.auth0.com/](https://manage.auth0.com/)
   - Set the Allowed Callback URLs to `http://localhost:3000/api/auth/callback`
   - Set the Allowed Logout URLs to `http://localhost:3000`
   - Copy the Auth0 domain, Client ID, and Client Secret

4. Configure environment variables:
   - Rename `.env.local.example` to `.env.local` (or create it if it doesn't exist)
   - Update the Auth0 environment variables:
     ```
     AUTH0_SECRET='a-long-random-string'
     AUTH0_BASE_URL='http://localhost:3000'
     AUTH0_ISSUER_BASE_URL='https://YOUR_AUTH0_DOMAIN'
     AUTH0_CLIENT_ID='YOUR_AUTH0_CLIENT_ID'
     AUTH0_CLIENT_SECRET='YOUR_AUTH0_CLIENT_SECRET'
     ```
   - Generate a strong random value for `AUTH0_SECRET` (this is used to encrypt the session cookie)

### Running the Application

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Features

- User authentication with Auth0
- Protected routes and pages
- User profile display
- Responsive design with Tailwind CSS

## Auth0 Integration

This application uses Auth0 for authentication and user management. The integration includes:

- Login and logout functionality
- User profile display
- Access token handling
- Session management

## Folder Structure

```
ranked-fintech/
├── app/                  # Next.js App Router
│   ├── api/              # API routes
│   │   └── auth/         # Auth0 API routes
│   ├── components/       # React components
│   │   └── auth/         # Auth components
│   ├── page.tsx          # Home page
│   └── layout.tsx        # Root layout
├── public/               # Static assets
├── .env.local            # Environment variables
└── package.json          # Dependencies and scripts
```

## Deployment

This application can be deployed to Vercel:

1. Push your code to GitHub
2. Import your repository to Vercel
3. Configure environment variables in Vercel project settings
4. Update Auth0 Allowed Callback URLs and Allowed Logout URLs with your production URL
