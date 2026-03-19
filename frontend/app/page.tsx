import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow">
        <nav className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-blue-600">JurystAi</div>
          <div className="space-x-4">
            <Link href="/auth/login" className="px-4 py-2 text-gray-600 hover:text-gray-900">
              Login
            </Link>
            <Link href="/auth/register" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Sign Up
            </Link>
          </div>
        </nav>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Legal AI for Kazakhstan
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Get instant answers to legal questions using RAG-powered AI trained on Kazakhstan legislation
        </p>
        <div className="space-x-4">
          <Link 
            href="/dashboard"
            className="inline-block px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
          >
            Start Now
          </Link>
          <Link
            href="/docs"
            className="inline-block px-8 py-3 bg-white text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 font-semibold"
          >
            Documentation
          </Link>
        </div>
      </main>

      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 border border-gray-200 rounded-lg">
              <div className="text-3xl mb-4">⚖️</div>
              <h3 className="text-xl font-semibold mb-2">Legal Codes</h3>
              <p className="text-gray-600">All 9 Kazakhstan legal codes indexed and searchable</p>
            </div>
            <div className="p-6 border border-gray-200 rounded-lg">
              <div className="text-3xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold mb-2">RAG System</h3>
              <p className="text-gray-600">Retrieval-Augmented Generation for accurate answers</p>
            </div>
            <div className="p-6 border border-gray-200 rounded-lg">
              <div className="text-3xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold mb-2">Real-time</h3>
              <p className="text-gray-600">Instant responses with source citations</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}