import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

function parseReportSections(report) {
  if (!report) return [];
  const lines = report.split('\n');
  const sections = [];
  let current = null;
  for (const line of lines) {
    const match = line.match(/^##\s+(.+)/);
    if (match) {
      if (current) sections.push(current);
      current = { title: match[1].trim(), content: '' };
    } else if (current) {
      current.content += line + '\n';
    }
  }
  if (current) sections.push(current);
  return sections;
}

function subtaskIcon(status) {
  switch (status) {
    case 'done': return '●';
    case 'failed': return '○';
    default: return '○';
  }
}

function CompanyCard({ companyName, report, subtasks }) {
  const initials = companyName
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const sections = useMemo(() => parseReportSections(report), [report]);

  const doneSubtasks = subtasks.filter((s) => s.status === 'done');
  const allDone = subtasks.length > 0 && doneSubtasks.length === subtasks.length;

  return (
    <motion.div
      layout
      className="bg-white rounded-3xl shadow-card border border-slate-100 overflow-hidden"
    >
      <div className="p-6 md:p-8">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 md:w-16 md:h-16 rounded-2xl bg-gradient-to-br from-brand-600 via-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-xl md:text-2xl font-bold shadow-glow flex-shrink-0">
            {initials}
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-xl md:text-2xl font-bold text-slate-900">{companyName}</h3>
              {allDone && (
                <span className="px-2.5 py-0.5 rounded-full bg-positive/10 text-positive text-xs font-semibold border border-positive/20">
                  Analysis Complete
                </span>
              )}
            </div>
            <p className="text-slate-500 text-sm">Competitive Intelligence Report</p>
            <p className="text-xs text-slate-400 mt-0.5">
              {subtasks.length} research dimensions &middot; AI-powered analysis
            </p>
          </div>
        </div>

        {/* Subtask tags */}
        {subtasks.length > 0 && (
          <div className="mt-5 flex flex-wrap gap-2">
            {subtasks.map((st) => (
              <span
                key={st.id}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium border flex items-center gap-1.5 ${
                  st.status === 'done'
                    ? 'bg-brand-50 text-brand-700 border-brand-100'
                    : st.status === 'failed'
                    ? 'bg-red-50 text-red-600 border-red-100'
                    : 'bg-slate-50 text-slate-400 border-slate-200'
                }`}
              >
                <span>{subtaskIcon(st.status)}</span>
                {st.description}
              </span>
            ))}
          </div>
        )}

        {/* Report Sections */}
        {sections.length > 0 && (
          <div className="mt-8 space-y-8">
            {sections.map((section, idx) => (
              <motion.div
                key={idx}
                className="pt-6 first:pt-0 border-t first:border-t-0 border-slate-100"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1, duration: 0.4 }}
              >
                <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-brand-100 text-brand-700 text-xs flex items-center justify-center font-bold">{idx + 1}</span>
                  {section.title.replace(/^\d+\.\s*/, '')}
                </h4>
                <div className="prose prose-sm prose-slate max-w-none space-y-3">
                  {section.content
                    .trim()
                    .split('\n')
                    .filter(Boolean)
                    .map((p, i) => (
                      <p key={i} className="text-slate-700 leading-relaxed">
                        {p}
                      </p>
                    ))}
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Research Notes (subtask results) */}
        {doneSubtasks.length > 0 && (
          <motion.div
            className="mt-8 pt-6 border-t border-slate-100"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.4 }}
          >
            <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
              Research Notes
            </h4>
            <div className="space-y-4">
              {doneSubtasks.map((st, idx) => (
                <motion.div
                  key={st.id}
                  className="p-4 rounded-xl bg-surface-secondary border border-slate-100"
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + idx * 0.08 }}
                >
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    {st.description}
                  </p>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {st.result || 'No data retrieved.'}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Bottom accent bar */}
      <div className="h-1 bg-gradient-to-r from-brand-500 via-violet-500 to-fuchsia-500" />
    </motion.div>
  );
}

export default CompanyCard;