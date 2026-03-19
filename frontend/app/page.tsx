export default function Home() {
  return (
    <div className='space-y-8'>
      <section className='text-center py-12'>
        <h2 className='text-4xl font-bold mb-4'>
          Kazakhstan Legal Legislation Search
        </h2>
        <p className='text-xl text-gray-600 mb-8'>
          AI-powered RAG system for fast and accurate legal document search
        </p>
        <div className='flex gap-4 justify-center'>
          <button className='bg-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700'>
            Sign In
          </button>
          <button className='border-2 border-primary text-primary px-6 py-3 rounded-lg font-semibold hover:bg-blue-50'>
            Sign Up
          </button>
        </div>
      </section>

      <section className='grid md:grid-cols-3 gap-6'>
        <div className='bg-white p-6 rounded-lg shadow'>
          <h3 className='text-xl font-semibold mb-2'>📚 Comprehensive</h3>
          <p>Access all 9 Kazakhstan legal codes in one place</p>
        </div>
        <div className='bg-white p-6 rounded-lg shadow'>
          <h3 className='text-xl font-semibold mb-2'>⚡ Fast</h3>
          <p>AI-powered search returns relevant results instantly</p>
        </div>
        <div className='bg-white p-6 rounded-lg shadow'>
          <h3 className='text-xl font-semibold mb-2'>🔒 Secure</h3>
          <p>Enterprise-grade security with JWT authentication</p>
        </div>
      </section>
    </div>
  );
}