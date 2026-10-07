import { useState } from 'react';
import TimetableSetup from './components/TimetableSetup';
import HolidaySetup from './components/HolidaySetup';
import JourneyPlanner from './components/JourneyPlanner';
import SavedResults from './components/SavedResults';

const TABS = [
  { key: 'planner', label: 'Journey Planner', comp: JourneyPlanner },
  { key: 'timetable', label: 'Timetable Patterns', comp: TimetableSetup },
  { key: 'holidays', label: 'Holidays', comp: HolidaySetup },
  { key: 'results', label: 'Saved Results', comp: SavedResults },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('planner');
  const ActiveComponent = TABS.find(t => t.key === activeTab).comp;

  return (
    <div className="app">
      <header>
        <h1>Delhi Metro Crowding Predictor</h1>
        <span className="planning-view-badge">Delhi Metro Planning View</span>
      </header>
      <nav className="tabs">
        {TABS.map(t => (
          <button key={t.key} className={activeTab === t.key ? 'active' : ''} onClick={() => setActiveTab(t.key)}>
            {t.label}
          </button>
        ))}
      </nav>
      <main>
        <ActiveComponent />
      </main>
    </div>
  );
}