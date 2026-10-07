import { useState, useEffect } from 'react';
import { listTimetablePatterns, createTimetablePattern, updateTimetablePattern, deleteTimetablePattern, listStations, createStation } from '../api';
import { DMRC_STATIONS } from '../stations';

const DAY_TYPES = ['weekday', 'weekend', 'holiday'];
const CROWDING_LEVELS = ['low', 'medium', 'high'];

export default function TimetableSetup() {
  const [patterns, setPatterns] = useState([]);
  const [stationMap, setStationMap] = useState({});
  const [idToName, setIdToName] = useState({});
  const [form, setForm] = useState({ origin: '', dest: '', day_type: 'weekday', start_time: '', end_time: '', baseline_crowding_level: 'low' });
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try {
      const [pData, sData] = await Promise.all([
        listTimetablePatterns({ limit: 100 }),
        listStations({ limit: 100 }),
      ]);
      setPatterns(pData.items);
      const nameToId = {};
      const idToName = {};
      sData.items.forEach(s => {
        nameToId[s.name] = s.id;
        idToName[s.id] = s.name;
      });
      setStationMap(nameToId);
      setIdToName(idToName);
    } catch {} finally { setLoading(false); }
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

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

  async function handleSave(e) {
    e.preventDefault();
    setError('');

    if (form.origin === form.dest) {
      setError('Origin and destination must be different stations.');
      return;
    }

    const originId = await ensureStation(form.origin);
    if (!originId) {
      setError(`Could not save "${form.origin}". Make sure the backend is running.`);
      return;
    }
    const destId = await ensureStation(form.dest);
    if (!destId) {
      setError(`Could not save "${form.dest}". Make sure the backend is running.`);
      return;
    }

    const body = {
      origin_station_id: originId,
      destination_station_id: destId,
      day_type: form.day_type,
      start_time: form.start_time,
      end_time: form.end_time,
      baseline_crowding_level: form.baseline_crowding_level,
    };

    try {
      if (editingId !== null) {
        await updateTimetablePattern(editingId, body);
        setEditingId(null);
      } else {
        await createTimetablePattern(body);
      }
      setForm({ origin: '', dest: '', day_type: 'weekday', start_time: '', end_time: '', baseline_crowding_level: 'low' });
      await load();
    } catch (err) {
      setError(err.data?.detail || 'Failed to save pattern');
    }
  }

  function handleEdit(p) {
    setEditingId(p.id);
    setForm({
      origin: idToName[p.origin_station_id] || '',
      dest: idToName[p.destination_station_id] || '',
      day_type: p.day_type,
      start_time: p.start_time,
      end_time: p.end_time,
      baseline_crowding_level: p.baseline_crowding_level,
    });
    setError('');
  }

  function handleCancelEdit() {
    setEditingId(null);
    setForm({ origin: '', dest: '', day_type: 'weekday', start_time: '', end_time: '', baseline_crowding_level: 'low' });
    setError('');
  }

  async function handleDelete(id) {
    setError('');
    try {
      await deleteTimetablePattern(id);
      await load();
    } catch (err) {
      setError(err.data?.detail || 'Failed to delete pattern');
    }
  }

  if (loading) return <div className="loading">Loading timetable patterns...</div>;

  return (
    <div className="section">
      <h2>Timetable Pattern Setup</h2>
      <form onSubmit={handleSave} className="pattern-form">
        <select name="origin" value={form.origin} onChange={handleChange} required>
          <option value="">Select origin</option>
          {DMRC_STATIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select name="dest" value={form.dest} onChange={handleChange} required>
          <option value="">Select destination</option>
          {DMRC_STATIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select name="day_type" value={form.day_type} onChange={handleChange}>
          {DAY_TYPES.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
        <input name="start_time" type="text" value={form.start_time} onChange={handleChange} placeholder="HH:MM" pattern="[0-2][0-9]:[0-5][0-9]" required />
        <input name="end_time" type="text" value={form.end_time} onChange={handleChange} placeholder="HH:MM" pattern="[0-2][0-9]:[0-5][0-9]" required />
        <select name="baseline_crowding_level" value={form.baseline_crowding_level} onChange={handleChange}>
          {CROWDING_LEVELS.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <button type="submit">{editingId !== null ? 'Update' : 'Add'}</button>
        {editingId !== null && <button type="button" onClick={handleCancelEdit}>Cancel</button>}
      </form>
      {error && <div className="error">{error}</div>}
      {patterns.length === 0 && <div className="empty">No timetable patterns yet.</div>}
      <ul className="item-list">
        {patterns.map(p => (
          <li key={p.id}>
            <span>{p.origin_station_name} → {p.destination_station_name} ({p.day_type}, {p.start_time}-{p.end_time}, {p.baseline_crowding_level})</span>
            <button onClick={() => handleEdit(p)}>Edit</button>
            <button onClick={() => handleDelete(p.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}