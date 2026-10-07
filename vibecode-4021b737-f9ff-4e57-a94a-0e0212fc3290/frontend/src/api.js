const BASE = import.meta.env.VITE_BASE_BE_ENDPOINT;

async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE}${path}`, opts);
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw { status: res.status, data };
  return data;
}

export function listStations(params) {
  const q = new URLSearchParams(params || {}).toString();
  return api('GET', `/api/stations?${q}`);
}

export function createStation(name) {
  return api('POST', '/api/stations', { name });
}

export function updateStation(id, name) {
  return api('PUT', `/api/stations/${id}`, { name });
}

export function deleteStation(id) {
  return api('DELETE', `/api/stations/${id}`);
}

export function listTimetablePatterns(params) {
  const q = new URLSearchParams(params || {}).toString();
  return api('GET', `/api/timetable-patterns?${q}`);
}

export function createTimetablePattern(data) {
  return api('POST', '/api/timetable-patterns', data);
}

export function updateTimetablePattern(id, data) {
  return api('PUT', `/api/timetable-patterns/${id}`, data);
}

export function deleteTimetablePattern(id) {
  return api('DELETE', `/api/timetable-patterns/${id}`);
}

export function listPublicHolidays(params) {
  const q = new URLSearchParams(params || {}).toString();
  return api('GET', `/api/public-holidays?${q}`);
}

export function createPublicHoliday(data) {
  return api('POST', '/api/public-holidays', data);
}

export function updatePublicHoliday(id, data) {
  return api('PUT', `/api/public-holidays/${id}`, data);
}

export function deletePublicHoliday(id) {
  return api('DELETE', `/api/public-holidays/${id}`);
}

export function createJourneyPrediction(data) {
  return api('POST', '/api/journey-predictions', data);
}

export function listSavedPredictionResults(params) {
  const q = new URLSearchParams(params || {}).toString();
  return api('GET', `/api/saved-prediction-results?${q}`);
}