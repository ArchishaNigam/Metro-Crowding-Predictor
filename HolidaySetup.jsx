import { useState, useEffect } from 'react';
import { listPublicHolidays, createPublicHoliday, updatePublicHoliday, deletePublicHoliday } from '../api';

export default function HolidaySetup() {
  const [holidays, setHolidays] = useState([]);
  const [calendarDate, setCalendarDate] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await listPublicHolidays({ limit: 100 });
      setHolidays(data.items);
    } catch {} finally { setLoading(false); }
  }

  async function handleSave(e) {
    e.preventDefault();
    setError('');
    try {
      if (editingId !== null) {
        await updatePublicHoliday(editingId, { calendar_date: calendarDate, display_name: displayName });
        setEditingId(null);
      } else {
        await createPublicHoliday({ calendar_date: calendarDate, display_name: displayName });
      }
      setCalendarDate('');
      setDisplayName('');
      await load();
    } catch (err) {
      setError(err.data?.detail || 'Failed to save holiday');
    }
  }

  function handleEdit(h) {
    setEditingId(h.id);
    setCalendarDate(h.calendar_date);
    setDisplayName(h.display_name);
    setError('');
  }

  function handleCancelEdit() {
    setEditingId(null);
    setCalendarDate('');
    setDisplayName('');
    setError('');
  }

  async function handleDelete(id) {
    setError('');
    try {
      await deletePublicHoliday(id);
      await load();
    } catch (err) {
      setError(err.data?.detail || 'Failed to delete holiday');
    }
  }

  if (loading) return <div className="loading">Loading holidays...</div>;

  return (
    <div className="section">
      <h2>Public Holiday Setup</h2>
      <form onSubmit={handleSave} className="inline-form">
        <input type="date" value={calendarDate} onChange={e => setCalendarDate(e.target.value)} required />
        <input value={displayName} onChange={e => setDisplayName(e.target.value)} placeholder="Holiday name" required />
        <button type="submit">{editingId !== null ? 'Update' : 'Add'}</button>
        {editingId !== null && <button type="button" onClick={handleCancelEdit}>Cancel</button>}
      </form>
      {error && <div className="error">{error}</div>}
      {holidays.length === 0 && <div className="empty">No holidays yet. Add one above.</div>}
      <ul className="item-list">
        {holidays.map(h => (
          <li key={h.id}>
            <span>{h.calendar_date} — {h.display_name}</span>
            <button onClick={() => handleEdit(h)}>Edit</button>
            <button onClick={() => handleDelete(h.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}