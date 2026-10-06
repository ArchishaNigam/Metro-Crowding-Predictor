import { useState, useEffect } from 'react';
import { listStations, createStation, updateStation, deleteStation } from '../api';
import { DMRC_STATIONS } from '../stations';

export default function StationSetup() {
  const [stations, setStations] = useState([]);
  const [selectedStation, setSelectedStation] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await listStations({ limit: 100 });
      setStations(data.items);
    } catch {} finally { setLoading(false); }
  }

  async function handleSave(e) {
    e.preventDefault();
    setError('');
    try {
      if (editingId !== null) {
        await updateStation(editingId, selectedStation);
        setEditingId(null);
      } else {
        await createStation(selectedStation);
      }
      setSelectedStation('');
      await load();
    } catch (err) {
      setError(err.data?.detail || 'Failed to save station');
    }
  }

  function handleEdit(station) {
    setEditingId(station.id);
    setSelectedStation(station.name);
    setError('');
  }

  function handleCancelEdit() {
    setEditingId(null);
    setSelectedStation('');
    setError('');
  }

  async function handleDelete(id) {
    setError('');
    try {
      await deleteStation(id);
      await load();
    } catch (err) {
      setError(err.data?.detail || 'Failed to delete station');
    }
  }

  if (loading) return <div className="loading">Loading stations...</div>;

  return (
    <div className="section">
      <h2>Station Setup</h2>
      <form onSubmit={handleSave} className="inline-form">
        <select value={selectedStation} onChange={e => setSelectedStation(e.target.value)} required>
          <option value="">Select a DMRC station...</option>
          {DMRC_STATIONS.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button type="submit">{editingId !== null ? 'Update' : 'Add'}</button>
        {editingId !== null && <button type="button" onClick={handleCancelEdit}>Cancel</button>}
      </form>
      {error && <div className="error">{error}</div>}
      {stations.length === 0 && <div className="empty">No stations yet. Add one above.</div>}
      <ul className="item-list">
        {stations.map(s => (
          <li key={s.id}>
            <span>{s.name}</span>
            <button onClick={() => handleEdit(s)}>Edit</button>
            <button onClick={() => handleDelete(s.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}