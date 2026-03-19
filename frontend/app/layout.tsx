import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "JurystAi - Legal AI for Kazakhstan",
  description: "RAG-based AI assistant for Kazakhstan legislation",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  )
}