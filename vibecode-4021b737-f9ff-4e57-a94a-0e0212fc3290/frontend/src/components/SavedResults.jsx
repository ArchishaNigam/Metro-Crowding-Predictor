import { useState, useEffect } from 'react';
import { listSavedPredictionResults } from '../api';

const CROWDING_LEVELS = ['low', 'medium', 'high'];

export default function SavedResults() {
  const [results, setResults] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, [filter]);

  async function load() {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (filter) params.crowding_level = filter;
      const data = await listSavedPredictionResults(params);
      setResults(data.items);
    } catch {} finally { setLoading(false); }
  }

  const hasResults = results.length > 0;

  return (
    <div className="section">
      <h2>Saved Prediction Results</h2>
      <div className="filter-bar">
        <label>Filter by crowding level: </label>
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="">All</option>
          {CROWDING_LEVELS.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      {loading && <div className="loading">Loading results...</div>}
      {!loading && !hasResults && (
        <div className="empty">
          {filter ? `No results with ${filter} crowding.` : 'No journey predictions have been created yet.'}
        </div>
      )}
      {!loading && hasResults && (
        <ul className="item-list">
          {results.map(r => (
            <li key={r.id}>
              <span>
                {r.origin_station_name} → {r.destination_station_name} | {r.journey_date} {r.planned_departure_time} | {r.derived_day_type} | {r.crowding_level}
              </span>
              {r.alert_text && <span className="alert-badge">Leave 20 minutes earlier</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}