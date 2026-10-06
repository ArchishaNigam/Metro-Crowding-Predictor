import { useState, useEffect } from 'react';
import { listStations, createStation, createJourneyPrediction } from '../api';
import { DMRC_STATIONS } from '../stations';

export default function JourneyPlanner() {
  const [stationMap, setStationMap] = useState({});
  const [originName, setOriginName] = useState('');
  const [destName, setDestName] = useState('');
  const [journeyDate, setJourneyDate] = useState('');
  const [plannedTime, setPlannedTime] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);

  useEffect(() => {
    listStations({ limit: 200 }).then(data => {
      const map = {};
      data.items.forEach(s => { map[s.name] = s.id; });
      setStationMap(map);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  async function ensureStation(name) {
    const id = stationMap[name];
    if (id) return id;
    try {
      const data = await createStation(name);
      stationMap[name] = data.id;
      return data.id;
    } catch {
      return null;
    }
  }

  async function handlePredict(e) {
    e.preventDefault();
    setError('');
    setResult(null);

    if (originName === destName) {
      setError('Origin and destination must be different stations.');
      return;
    }

    setPredicting(true);

    const originId = await ensureStation(originName);
    if (!originId) {
      setError(`Could not save "${originName}". Make sure the backend is running.`);
      setPredicting(false);
      return;
    }
    const destId = await ensureStation(destName);
    if (!destId) {
      setError(`Could not save "${destName}". Make sure the backend is running.`);
      setPredicting(false);
      return;
    }

    try {
      const data = await createJourneyPrediction({
        origin_station_id: originId,
        destination_station_id: destId,
        journey_date: journeyDate,
        planned_departure_time: plannedTime,
      });
      setResult(data);
    } catch (err) {
      setError(err.data?.detail || 'Failed to get prediction');
    } finally { setPredicting(false); }
  }

  return (
    <div className="section">
      <h2>Journey Planner</h2>
      <form onSubmit={handlePredict} className="planner-form">
        <select value={originName} onChange={e => setOriginName(e.target.value)} required>
          <option value="">Origin station</option>
          {DMRC_STATIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={destName} onChange={e => setDestName(e.target.value)} required>
          <option value="">Destination station</option>
          {DMRC_STATIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <input type="date" value={journeyDate} onChange={e => setJourneyDate(e.target.value)} required />
        <input type="time" value={plannedTime} onChange={e => setPlannedTime(e.target.value)} required />
        <button type="submit" disabled={predicting}>{predicting ? 'Predicting...' : 'Get Prediction'}</button>
      </form>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="prediction-result">
          {!result.prediction_available && <div className="no-prediction">No prediction available</div>}
          {result.prediction_available && (
            <>
              <p><strong>Journey:</strong> {result.origin_station_name} → {result.destination_station_name}</p>
              <p><strong>Date:</strong> {result.journey_date}</p>
              <p><strong>Planned departure:</strong> {result.planned_departure_time}</p>
              <p><strong>Day type:</strong> {result.derived_day_type}</p>
              <p><strong>Crowding level:</strong> {result.crowding_level}</p>
              {result.is_leave_earlier_alert_shown && (
                <div className="alert">
                  <strong>{result.alert_text}</strong>
                  <p>Suggested departure: {result.suggested_departure_date} at {result.suggested_departure_time}</p>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}