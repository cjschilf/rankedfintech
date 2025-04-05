import Profile from "./components/auth/Profile";

export default function Home() {
  return (
    <div className="grid grid-rows-[auto_1fr_auto] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <header className="w-full flex justify-between items-center py-4">
        <h1 className="text-3xl font-bold">Ranked Fintech</h1>
        <Profile />
      </header>
      
      <main className="flex flex-col gap-[32px] items-center text-center">
        <h2 className="text-2xl font-bold">Welcome to Ranked Fintech</h2>
        <p className="max-w-2xl">
          Your platform for financial analysis and ranking. Sign in to access personalized insights
          and financial tools designed to help you make better investment decisions.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-2">Market Rankings</h3>
            <p>Explore top-performing assets across different markets and categories.</p>
          </div>
          
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-2">Portfolio Analysis</h3>
            <p>Track and analyze your investments with advanced portfolio tools.</p>
          </div>
          
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-2">Personalized Insights</h3>
            <p>Get tailored financial recommendations based on your goals.</p>
          </div>
        </div>
      </main>
      
      <footer className="w-full py-6 text-center text-sm text-gray-600 dark:text-gray-400">
        <p>© {new Date().getFullYear()} Ranked Fintech. All rights reserved.</p>
      </footer>
    </div>
  );
}
