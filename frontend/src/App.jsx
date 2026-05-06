import React, { useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import CompanyCard from './components/CompanyCard';
import { mockCompanies } from './mockData';
import { AnimatePresence, motion } from 'framer-motion';

function App() {
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (name) => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 800));
    const key = name.toLowerCase();
    const data = mockCompanies[key] || generateMock(name);
    setCompany(data);
    setLoading(false);
  };

  const generateMock = (name) => {
    return {
      name,
      industry: 'Technology',
      founded: '2020',
      hq: 'San Francisco, CA',
      employees: '200+',
      recentFunding: '$10M (Series A)',
      valuation: '$50M+',
      tags: ['AI', 'SaaS'],
      sentimentScore: Math.floor(Math.random() * 30) + 70,
      sentimentBreakdown: { positive: 70, neutral: 20, negative: 10 },
      news: [],
      growthRate: '+30%',
      marketPos: 'Emerging Player',
      hiringTrend: { openRoles: 42 },
    };
  };

  return (
    <div className="min-h-screen bg-surface-secondary bg-radial-glow bg-grid">
      <Header />
      <main className="max-w-5xl mx-auto px-4 md:px-6 pb-20">
        <SearchBar onSearch={handleSearch} loading={loading} />
        <AnimatePresence mode="wait">
          {company && (
            <motion.div
              key={company.name}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
            >
              <CompanyCard data={company} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="border-t border-slate-200 py-8 text-center">
        <p className="text-sm text-slate-400">
          &copy; {new Date().getFullYear()} CompetiSight. Built for strategic advantage.
        </p>
        <div className="flex justify-center gap-6 mt-3">
          <a href="#" className="text-xs text-slate-400 hover:text-slate-600 transition-colors">Privacy</a>
          <a href="#" className="text-xs text-slate-400 hover:text-slate-600 transition-colors">Terms</a>
          <a href="#" className="text-xs text-slate-400 hover:text-slate-600 transition-colors">Contact</a>
        </div>
      </footer>
    </div>
  );
}

export default App;