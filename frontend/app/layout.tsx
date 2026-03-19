import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'JurystAi - Legal AI Assistant',
  description: 'Kazakhstan legislation RAG system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang='en'>
      <body className='bg-gray-50 text-gray-900'>
        <nav className='bg-white shadow'>
          <div className='max-w-7xl mx-auto px-4 py-4'>
            <h1 className='text-2xl font-bold text-primary'>JurystAi</h1>
          </div>
        </nav>
        <main className='max-w-7xl mx-auto p-4'>
          {children}
        </main>
      </body>
    </html>
  );
}