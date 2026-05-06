import React from 'react';
import { motion } from 'framer-motion';

const statusIcon = {
  pending: { icon: '○', label: 'Queued', color: 'text-slate-400' },
  in_progress: { icon: '◌', label: 'Researching…', color: 'text-brand-600' },
  done: { icon: '●', label: 'Done', color: 'text-positive' },
  failed: { icon: '○', label: 'Failed', color: 'text-negative' },
};

function ProgressPanel({ subtasks, companyName }) {
  const doneCount = subtasks.filter((s) => s.status === 'done' || s.status === 'failed').length;
  const total = Math.max(subtasks.length, 1);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="mx-auto max-w-xl mt-8"
    >
      <div className="bg-white rounded-2xl shadow-card border border-slate-100 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-brand-100 flex items-center justify-center">
            <svg className="animate-spin w-5 h-5 text-brand-600" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">Analyzing {companyName}</h3>
            <p className="text-xs text-slate-400">
              {doneCount}/{total} research tasks completed
            </p>
          </div>
        </div>

        <div className="w-full bg-slate-100 rounded-full h-2 mb-5 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-brand-500 to-violet-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${(doneCount / total) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>

        <div className="space-y-2">
          {subtasks.map((st) => {
            const info = statusIcon[st.status] || statusIcon.pending;
            return (
              <motion.div
                key={st.id}
                className="flex items-center gap-3 text-sm"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: st.id * 0.05 }}
              >
                <span className={`text-lg ${info.color}`}>{info.icon}</span>
                <span className="flex-1 text-slate-700 truncate">{st.description}</span>
                <span className={`text-xs font-medium ${info.color}`}>{info.label}</span>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

export default ProgressPanel;