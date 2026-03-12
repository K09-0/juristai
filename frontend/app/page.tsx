'use client'

import { useState } from 'react'
import { Scale, FileText, Mic, Search, Shield, Zap, Lock, CreditCard, Menu, X, ChevronRight, Star, CheckCircle } from 'lucide-react'

export default function Home() {
  const [query, setQuery] = useState('')
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('search')

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Glass Header */}
      <header className="fixed w-full top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25 group-hover:shadow-blue-500/40 transition-all">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">JuristAI</span>
            </div>
            
            <nav className="hidden md:flex gap-8">
              {['Возможности', 'Тарифы', 'API'].map((item) => (
                <a key={item} href={`#${item.toLowerCase()}`} className="text-sm text-slate-400 hover:text-white transition-colors relative group">
                  {item}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-500 group-hover:w-full transition-all"></span>
                </a>
              ))}
            </nav>

            <div className="flex items-center gap-4">
              <button className="hidden md:flex px-4 py-2 text-sm text-slate-300 hover:text-white transition">
                Вход
              </button>
              <button className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-sm font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all hover:scale-105">
                Начать бесплатно
              </button>
            </div>

            <button className="md:hidden text-slate-400" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-32 pb-20 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-sm text-slate-400">Работает с законодательством РК 2024</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Юридический AI{' '}
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              нового поколения
            </span>
          </h1>
          
          <p className="text-xl text-slate-400 mb-12 max-w-2xl mx-auto">
            Мгновенные ответы из ГК, ТК, КоАП РК. Генерация документов. 
            Анализ договоров с AI-разметкой рисков.
          </p>

          {/* Interactive Search */}
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2 p-1.5 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10">
              {[
                { id: 'search', icon: Search, label: 'Поиск' },
                { id: 'doc', icon: FileText, label: 'Документ' },
                { id: 'audio', icon: Mic, label: 'Аудио' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    activeTab === tab.id 
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25' 
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="mt-4 relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition"></div>
              <div className="relative flex items-center bg-slate-900 rounded-2xl border border-white/10 p-2">
                <Search className="w-5 h-5 text-slate-500 ml-4" />
                <input 
                  type="text" 
                  placeholder={
                    activeTab === 'search' ? "Какие сроки исковой давности по договору подряда?" :
                    activeTab === 'doc' ? "Опишите ситуацию для генерации документа..." :
                    "Загрузите аудиозапись судебного заседания..."
                  }
                  className="flex-1 bg-transparent px-4 py-4 text-white placeholder:text-slate-500 outline-none"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
                <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all flex items-center gap-2">
                  {activeTab === 'audio' ? 'Загрузить' : 'Спросить'}
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex flex-wrap justify-center gap-3 mt-6 text-sm text-slate-500">
              <span>Популярное:</span>
              {['Неустойка по 395 ГК', 'Увольнение по ТК', 'Регистрация ТОО', 'Алименты'].map((tag) => (
                <button key={tag} className="px-3 py-1 rounded-full bg-white/5 hover:bg-white/10 transition border border-white/5">
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="relative z-10 border-y border-white/10 bg-white/5 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[['10K+', 'Юристов'], ['50K+', 'Документов'], ['99%', 'Точность'], ['24/7', 'Доступность']].map(([num, label]) => (
              <div key={label}>
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">{num}</div>
                <div className="text-sm text-slate-400 mt-1">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="возможности" className="relative z-10 py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Возможности</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">Всё необходимое для юридической работы в одном сервисе</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Search, title: 'RAG-поиск', desc: 'Нейросеть ищет ответы в 50+ НПА РК', free: true, color: 'blue' },
              { icon: FileText, title: 'Генерация документов', desc: 'Иски, претензии, договоры в 4 тонах', free: true, color: 'purple' },
              { icon: Shield, title: 'Анализ договоров', desc: 'AI находит риски и предлагает правки', premium: true, color: 'pink' },
              { icon: Mic, title: 'Audio-to-Law', desc: 'Транскрибация судебных заседаний', premium: true, color: 'orange' },
              { icon: Zap, title: 'Безлимит Premium', desc: 'Неограниченные запросы 24/7', premium: true, color: 'green' },
              { icon: Lock, title: 'Безопасность', desc: 'Шифрование данных и локальное хранение', free: true, color: 'cyan' },
            ].map((feature, i) => (
              <div key={i} className="group relative p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all hover:-translate-y-1">
                <div className={`w-12 h-12 rounded-xl bg-${feature.color}-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className={`w-6 h-6 text-${feature.color}-400`} />
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-bold text-lg">{feature.title}</h3>
                  {feature.premium && <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />}
                </div>
                <p className="text-slate-400 text-sm">{feature.desc}</p>
                <div className="mt-4 flex items-center gap-2 text-xs">
                  <span className={`px-2 py-1 rounded-full ${feature.free ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                    {feature.free ? 'Бесплатно' : 'Premium'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="тарифы" className="relative z-10 py-24 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Тарифы</h2>
            <p className="text-slate-400">Начните бесплатно, обновитесь когда понадобится больше</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Free */}
            <div className="relative p-8 rounded-3xl bg-white/5 border border-white/10">
              <h3 className="text-xl font-semibold mb-2">Старт</h3>
              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-5xl font-bold">0</span>
                <span className="text-slate-400">₸/мес</span>
              </div>
              
              <ul className="space-y-4 mb-8">
                {['10 запросов/день в законы', 'Базовая генерация документов', 'Email-поддержка'].map((item) => (
                  <li key={item} className="flex items-center gap-3 text-slate-300">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    {item}
                  </li>
                ))}
                {['Аудио транскрибация', 'Анализ договоров', 'Приоритетная поддержка'].map((item) => (
                  <li key={item} className="flex items-center gap-3 text-slate-600">
                    <Lock className="w-5 h-5" />
                    {item}
                  </li>
                ))}
              </ul>

              <button className="w-full py-4 rounded-xl border border-white/20 font-semibold hover:bg-white/5 transition">
                Начать бесплатно
              </button>
            </div>

            {/* Premium */}
            <div className="relative p-8 rounded-3xl bg-gradient-to-b from-blue-600/20 to-purple-600/20 border border-blue-500/50 overflow-hidden">
              <div className="absolute top-0 right-0 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold px-4 py-1 rounded-bl-xl">
                POPULAR
              </div>
              
              <h3 className="text-xl font-semibold mb-2 text-blue-400">Premium</h3>
              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">5 000</span>
                <span className="text-slate-400">₸/мес</span>
              </div>

              <ul className="space-y-4 mb-8">
                {['Безлимитные запросы', 'Все тона документов', 'Audio-to-Law транскрибация', 'Анализ договоров с разметкой', 'Приоритетная поддержка 24/7', 'API доступ'].map((item) => (
                  <li key={item} className="flex items-center gap-3 text-slate-200">
                    <CheckCircle className="w-5 h-5 text-blue-400" />
                    {item}
                  </li>
                ))}
              </ul>

              <button className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all hover:scale-[1.02]">
                Оформить Premium
              </button>
              
              <p className="text-center text-xs text-slate-500 mt-4">
                Оплата через Kaspi. Активация в течение 2 часов.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="p-12 rounded-3xl bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-white/10">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Готовы начать?</h2>
            <p className="text-slate-400 mb-8 max-w-xl mx-auto">
              Присоединяйтесь к тысячам юристов, которые уже используют JuristAI для работы с законодательством РК
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-8 py-4 bg-white text-slate-950 rounded-xl font-bold hover:bg-slate-200 transition">
                Бесплатный доступ
              </button>
              <button className="px-8 py-4 border border-white/20 rounded-xl font-semibold hover:bg-white/5 transition">
                Связаться с нами
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-12 px-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Scale className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold">JuristAI</span>
          </div>
          
          <div className="text-sm text-slate-500">
            © 2024 JuristAI. Не является юридической консультацией.
          </div>

          <div className="flex gap-6 text-sm text-slate-400">
            <a href="#" className="hover:text-white transition">Политика</a>
            <a href="#" className="hover:text-white transition">Условия</a>
            <a href="#" className="hover:text-white transition">API</a>
          </div>
        </div>
      </footer>
    </div>
  )
}