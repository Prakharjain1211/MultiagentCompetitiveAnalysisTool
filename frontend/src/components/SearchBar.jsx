import React, { useState } from 'react';

function SearchBar({ onSearch, loading }) {
  const [value, setValue] = useState('');
  const [focused, setFocused] = useState(false);
  const suggestions = ['OpenAI', 'Stripe', 'Figma', 'Databricks', 'Anthropic', 'Notion'];

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (trimmed) {
      onSearch(trimmed);
    }
  };

  return (
    <section className="relative pt-8 pb-10 text-center">
      <div className="relative z-10">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-medium mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-positive animate-pulse" />
          AI-Powered Competitive Intelligence
        </div>

        <h2 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 leading-[1.1] mb-4">
          Competitive Intelligence,{' '}
          <span className="gradient-text">Delivered Instantly</span>
        </h2>
        <p className="text-slate-500 text-lg max-w-xl mx-auto mb-8">
          Uncover real‑time insights on any company — funding, strategy, market moves, and more in seconds.
        </p>

        <form onSubmit={handleSubmit} className="flex justify-center items-center gap-2 max-w-xl mx-auto">
          <div className={`
            relative flex-1 transition-all duration-300
            ${focused ? 'ring-4 ring-brand-100 scale-[1.02]' : ''}
            rounded-2xl
          `}>
            <svg
              className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <input
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              placeholder="Search any company..."
              className="w-full pl-12 pr-4 py-3.5 rounded-2xl border border-slate-200 bg-white shadow-sm text-slate-900 placeholder-slate-400 focus:outline-none transition-all text-base"
              disabled={loading}
            />
            {value && (
              <button
                type="button"
                onClick={() => setValue('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            )}
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-7 py-3.5 bg-brand-600 text-white font-semibold rounded-2xl hover:bg-brand-700 disabled:opacity-60 transition-all hover:shadow-glow active:scale-[0.98] flex items-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Analyzing
              </>
            ) : (
              <>
                Analyze
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </>
            )}
          </button>
        </form>

        <div className="mt-6 flex flex-wrap justify-center gap-2">
          {suggestions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => onSearch(s)}
              className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-600 hover:text-brand-600 hover:border-brand-200 hover:bg-brand-50 transition-all active:scale-95"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

export default SearchBar;