import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import CompanyCard from './components/CompanyCard';
import ProgressPanel from './components/ProgressPanel';
import { submitAnalysis, getAnalysisStatus } from './api';
import { AnimatePresence, motion } from 'framer-motion';

function App() {
  const [companyName, setCompanyName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisStatus, setAnalysisStatus] = useState('idle');
  const [report, setReport] = useState('');
  const [subtasks, setSubtasks] = useState([]);
  const [runId, setRunId] = useState(null);
  const pollingRef = useRef(null);

  const handleSearch = async (name) => {
    setCompanyName(name);
    setLoading(true);
    setError(null);
    setAnalysisStatus('pending');
    setSubtasks([]);
    setReport('');
    setRunId(null);

    try {
      const { run_id } = await submitAnalysis(name);
      setRunId(run_id);

      const poll = async () => {
        const result = await getAnalysisStatus(run_id);
        if (!result) return;

        setAnalysisStatus(result.status);
        setSubtasks(result.subtasks || []);

        if (result.status === 'completed') {
          setReport(result.report);
          setLoading(false);
          clearInterval(pollingRef.current);
        } else if (result.status === 'error') {
          setError(result.errors?.join(', ') || 'Analysis failed');
          setLoading(false);
          clearInterval(pollingRef.current);
        }
      };

      pollingRef.current = setInterval(poll, 2000);
      poll();
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const showResults = analysisStatus === 'completed' && report;
  const showProgress = (analysisStatus === 'pending' || analysisStatus === 'running') && runId;

  return (
    <div className="min-h-screen bg-surface-secondary bg-radial-glow bg-grid">
      <Header />
      <main className="max-w-5xl mx-auto px-4 md:px-6 pb-20">
        <SearchBar onSearch={handleSearch} loading={loading} />

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mx-auto max-w-xl mt-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-700 text-sm text-center"
          >
            {error}
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {showProgress && !showResults && (
            <ProgressPanel subtasks={subtasks} companyName={companyName} />
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {showResults && (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
            >
              <CompanyCard companyName={companyName} report={report} subtasks={subtasks} />
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