import React from 'react';

function Header() {
  return (
    <header className="glass sticky top-0 z-50 border-b border-white/20">
      <div className="max-w-6xl mx-auto flex justify-between items-center px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-600 to-violet-500 flex items-center justify-center shadow-glow">
            <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <span className="text-xl font-bold tracking-tight text-slate-900">
            Competi<span className="text-brand-600">Sight</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
            <a href="#" className="hover:text-slate-900 transition-colors">Dashboard</a>
            <a href="#" className="hover:text-slate-900 transition-colors">Reports</a>
            <a href="#" className="hover:text-slate-900 transition-colors">Compare</a>
          </nav>
          <button className="px-5 py-2.5 bg-slate-900 text-white text-sm font-medium rounded-xl hover:bg-slate-800 transition-all hover:shadow-lg active:scale-[0.98]">
            Get Started
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;