'use client'

import { useState } from 'react'
import { Scale, FileText, Mic, Search, Shield, Zap, Lock, CreditCard, Menu, X } from 'lucide-react'

export default function Home() {
  const [query, setQuery] = useState('')
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const features = [
    { icon: <Search className="w-6 h-6" />, title: "Поиск по законам РК", desc: "Мгновенные ответы из ГК, ТК, КоАП и других НПА", free: true },
    { icon: <FileText className="w-6 h-6" />, title: "Генерация документов", desc: "Иски, претензии, договоры в 4 тонах голоса", free: true },
    { icon: <Mic className="w-6 h-6" />, title: "Audio-to-Law", desc: "Транскрибация судебных заседаний", premium: true },
    { icon: <Shield className="w-6 h-6" />, title: "Анализ договоров", desc: "Auto-redlining: найдём все риски", premium: true },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Scale className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">JuristAI</span>
            </div>
            
            <nav className="hidden md:flex gap-6">
              <a href="#features" className="text-gray-600 hover:text-blue-600">Возможности</a>
              <a href="#pricing" className="text-gray-600 hover:text-blue-600">Тарифы</a>
              <a href="/login" className="text-gray-600 hover:text-blue-600">Вход</a>
            </nav>

            <button className="md:hidden" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Юридический AI для <span className="text-blue-600">Казахстана</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Мгновенные ответы из законодательства РК. Генерация документов. 
            Анализ договоров. Всё в одном сервисе.
          </p>
          
          {/* Search Box */}
          <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-2 flex gap-2">
            <input 
              type="text" 
              placeholder="Задайте юридический вопрос..."
              className="flex-1 px-4 py-3 rounded-xl border-0 focus:ring-2 focus:ring-blue-500 outline-none"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition">
              <Search className="w-5 h-5" />
            </button>
          </div>
          
          <p className="text-sm text-gray-500 mt-4">
            Например: "Какие сроки исковой давности по договору подряда?"
          </p>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Возможности</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f, i) => (
              <div key={i} className={`p-6 rounded-2xl border-2 ${f.premium ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200'}`}>
                <div className="text-blue-600 mb-3">{f.icon}</div>
                <h3 className="font-bold mb-2 flex items-center gap-2">
                  {f.title}
                  {f.premium && <span className="text-xs bg-yellow-400 text-black px-2 py-0.5 rounded">PREMIUM</span>}
                </h3>
                <p className="text-sm text-gray-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Тарифы</h2>
          <div className="grid md:grid-cols-2 gap-8">
            {/* Free */}
            <div className="bg-white p-8 rounded-2xl shadow-lg border-2 border-gray-200">
              <h3 className="text-xl font-bold mb-4">Бесплатный</h3>
              <div className="text-4xl font-bold mb-6">0 ₸</div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2"><Zap className="w-4 h-4 text-green-500" /> 10 запросов/день в законы</li>
                <li className="flex items-center gap-2"><FileText className="w-4 h-4 text-green-500" /> Базовая генерация документов</li>
                <li className="flex items-center gap-2 text-gray-400"><Lock className="w-4 h-4" /> Без аудио и анализа договоров</li>
              </ul>
              <button className="w-full py-3 rounded-xl border-2 border-blue-600 text-blue-600 font-semibold hover:bg-blue-50">
                Начать бесплатно
              </button>
            </div>

            {/* Premium */}
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-8 rounded-2xl shadow-lg text-white">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <CreditCard className="w-5 h-5" /> Premium
              </h3>
              <div className="text-4xl font-bold mb-6">5 000 ₸<span className="text-lg font-normal">/мес</span></div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2"><Zap className="w-4 h-4" /> Безлимитные запросы</li>
                <li className="flex items-center gap-2"><Mic className="w-4 h-4" /> Audio-to-Law транскрибация</li>
                <li className="flex items-center gap-2"><Shield className="w-4 h-4" /> Анализ договоров с разметкой</li>
                <li className="flex items-center gap-2"><FileText className="w-4 h-4" /> Все тона документов</li>
              </ul>
              <button className="w-full py-3 rounded-xl bg-yellow-400 text-gray-900 font-bold hover:bg-yellow-300">
                Оформить Premium
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Scale className="w-6 h-6" />
            <span className="text-lg font-bold">JuristAI</span>
          </div>
          <p className="text-gray-400">Юридический AI-ассистент для Республики Казахстан</p>
          <p className="text-gray-500 text-sm mt-4">© 2024 JuristAI. Не является юридической консультацией.</p>
        </div>
      </footer>
    </div>
  )
}
