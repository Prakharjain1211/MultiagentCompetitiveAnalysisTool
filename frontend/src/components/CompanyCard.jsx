import React from 'react';
import { motion } from 'framer-motion';

function sentimentColor(score) {
  if (score >= 75) return 'positive';
  if (score >= 55) return 'neutral';
  return 'negative';
}

function SentimentRing({ score, color }) {
  const colors = {
    positive: { stroke: '#10b981', bg: '#ecfdf5', text: 'text-positive' },
    neutral: { stroke: '#f59e0b', bg: '#fffbeb', text: 'text-neutral' },
    negative: { stroke: '#ef4444', bg: '#fef2f2', text: 'text-negative' },
  };
  const c = colors[color];
  const circumference = 2 * Math.PI * 28;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex items-center gap-2">
      <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
        <circle cx="32" cy="32" r="28" fill="none" stroke={c.bg === '#ecfdf5' ? '#d1fae5' : c.bg === '#fffbeb' ? '#fef3c7' : '#fee2e2'} strokeWidth="6" />
        <motion.circle
          cx="32" cy="32" r="28"
          fill="none"
          stroke={c.stroke}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      <div>
        <p className={`text-xl font-bold ${c.text}`}>{score}%</p>
        <p className="text-xs text-slate-400 font-medium">Sentiment</p>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, trend }) {
  return (
    <motion.div
      className="group bg-surface-secondary rounded-2xl p-4 hover:bg-brand-50 transition-colors border border-slate-100 hover:border-brand-100 cursor-default"
      whileHover={{ scale: 1.02 }}
      transition={{ type: 'spring', stiffness: 400, damping: 20 }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">{icon}</span>
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</p>
      </div>
      <p className="text-lg font-semibold text-slate-900 mb-1">{value}</p>
      {trend && <p className="text-xs text-positive font-medium">{trend}</p>}
    </motion.div>
  );
}

function CompanyCard({ data }) {
  const {
    name,
    industry,
    hq,
    employees,
    founded,
    tags,
    sentimentScore,
    recentFunding,
    growthRate,
    marketPos,
    hiringTrend,
    news,
  } = data;

  const initials = name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const color = sentimentColor(sentimentScore);

  return (
    <motion.div
      layout
      className="bg-white rounded-3xl shadow-card border border-slate-100 overflow-hidden"
    >
      <div className="p-6 md:p-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 md:w-16 md:h-16 rounded-2xl bg-gradient-to-br from-brand-600 via-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-xl md:text-2xl font-bold shadow-glow flex-shrink-0">
              {initials}
            </div>
            <div>
              <h3 className="text-xl md:text-2xl font-bold text-slate-900">{name}</h3>
              <p className="text-slate-500 text-sm">{industry} &middot; {hq}</p>
              <p className="text-slate-400 text-xs mt-0.5">
                {employees} employees &middot; Founded {founded}
              </p>
            </div>
          </div>
          <SentimentRing score={sentimentScore} color={color} />
        </div>

        {/* Tags */}
        <div className="mt-5 flex flex-wrap gap-2">
          {tags.map((t, i) => (
            <span
              key={i}
              className="px-3 py-1.5 bg-brand-50 text-brand-700 rounded-xl text-xs font-medium border border-brand-100"
            >
              {t}
            </span>
          ))}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-6">
          <StatCard icon="💰" label="Funding" value={recentFunding.split('(')[0].trim()} trend={recentFunding.includes('(') ? recentFunding.match(/\((.*?)\)/)?.[1] : null} />
          <StatCard icon="📈" label="Growth Rate" value={growthRate} />
          <StatCard icon="🏆" label="Market Position" value={marketPos} />
          <StatCard icon="💼" label="Open Roles" value={hiringTrend?.openRoles ?? '-'} trend={hiringTrend?.openRoles > 100 ? 'Hiring actively' : null} />
        </div>

        {/* News Section */}
        {news && news.length > 0 && (
          <motion.div
            className="mt-6 pt-6 border-t border-slate-100"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.4 }}
          >
            <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Latest News
            </h4>
            <div className="space-y-3">
              {news.slice(0, 4).map((n, idx) => (
                <motion.div
                  key={idx}
                  className="group flex gap-4 p-3 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer"
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + idx * 0.1 }}
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-brand-400 mt-2 flex-shrink-0 group-hover:scale-150 transition-transform" />
                  <div>
                    <p className="font-medium text-sm text-slate-800 group-hover:text-brand-700 transition-colors">{n.title}</p>
                    <p className="text-xs text-slate-400 mt-1">{n.desc}</p>
                    {n.date && <p className="text-xs text-slate-300 mt-1">{n.date}</p>}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Bottom accent bar */}
      <div className={`h-1 bg-${color === 'positive' ? 'positive' : color === 'neutral' ? 'neutral' : 'negative'}`} />
    </motion.div>
  );
}

export default CompanyCard;