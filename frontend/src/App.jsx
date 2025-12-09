import { useState } from 'react'
import Dashboard from './components/Dashboard'
import { Activity } from 'lucide-react'

function App() {
  const [darkMode, setDarkMode] = useState(true)

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-3">
                <Activity className="h-8 w-8 text-primary-600 dark:text-primary-400" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    CV-Mindcare
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Wellness Monitoring Dashboard
                  </p>
                </div>
              </div>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-gray-900 dark:text-white"
              >
                {darkMode ? '☀️ Light' : '🌙 Dark'}
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Dashboard />
        </main>

        {/* Footer */}
        <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-sm text-gray-500 dark:text-gray-400">
              CV-Mindcare v0.2.0 - Privacy-first local wellness monitoring
            </p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
