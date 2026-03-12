export const metadata = {
  title: 'JuristAI - Юридический AI для Казахстана',
  description: 'Мгновенные ответы из законодательства РК, генерация документов, анализ договоров',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
}
