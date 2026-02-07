export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          NCR Voyix Inventory Health Dashboard
        </h1>
        
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold mb-4">🚀 Project Status</h2>
          <p className="text-gray-700 mb-4">
            The project structure is complete and ready for implementation.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="border border-green-200 bg-green-50 rounded-lg p-4">
              <h3 className="font-semibold text-green-800 mb-2">✅ Backend Running</h3>
              <p className="text-sm text-green-700">
                FastAPI server is live at <code className="bg-green-100 px-2 py-1 rounded">localhost:8000</code>
              </p>
              <a 
                href="http://localhost:8000/docs" 
                target="_blank"
                className="text-blue-600 hover:underline text-sm mt-2 inline-block"
              >
                View API Docs →
              </a>
            </div>
            
            <div className="border border-blue-200 bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-800 mb-2">✅ Frontend Running</h3>
              <p className="text-sm text-blue-700">
                Next.js app is live at <code className="bg-blue-100 px-2 py-1 rounded">localhost:3000</code>
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-4">📋 Next Steps</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>Create database models (SQLAlchemy ORM)</li>
            <li>Build demo data generator with realistic patterns</li>
            <li>Implement core services (forecasting, anomaly detection, transfers)</li>
            <li>Create API endpoints</li>
            <li>Build frontend pages and components</li>
          </ol>
        </div>

        <div className="mt-8 text-center text-gray-600">
          <p>Check <code className="bg-gray-100 px-2 py-1 rounded">STATUS.md</code> for detailed progress</p>
        </div>
      </div>
    </main>
  )
}
