export async function submitAnalysis(company, model = 'gpt-4o-mini') {
  const res = await fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ company, model }),
  });
  if (!res.ok) throw new Error(`Analysis request failed: ${res.status}`);
  return res.json();
}

export async function getAnalysisStatus(runId) {
  const res = await fetch(`/analyze/${runId}`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error(`Status check failed: ${res.status}`);
  }
  return res.json();
}