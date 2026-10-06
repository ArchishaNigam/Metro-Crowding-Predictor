# Metro-Crowding-Predictor
A sandbox-safe planning product that models predicted crowding at Delhi Metro stations from locally maintained timetables and public-holiday dates, and shows an in-app leave-earlier alert when a selected journey is predicted to be congested.

Problem: Delhi Metro riders need a simple way to see predicted station congestion for a planned trip using available timetable patterns and public-holiday context. The first version must operate entirely on local, manually maintained data and provide an in-app advisory such as “Leave 20 minutes earlier” rather than sending messages outside the product.

Goals:

Let a commuter select an origin, destination, travel date, and planned departure time for a Delhi Metro journey.
Allow an operating-context selector labelled as Delhi Metro Planning View, without authentication or access control, to separate locally maintained planning data from commuter use.
Maintain local station, timetable-pattern, and public-holiday records that drive predictions.
Display a deterministic predicted crowding level and supporting timetable/holiday facts for a planned journey.
Show an in-app “Leave 20 minutes earlier” alert only under a defined high-crowding condition.
Allow correction of local source records so future predictions use the corrected facts.

Main features:
Local Delhi Metro station management
Timetable-pattern management by station pair, day type, time range, and baseline crowding
Public-holiday calendar management
Journey prediction planner with deterministic timetable matching
In-app high-crowding leave-earlier alert
Prediction result history with crowding filter and empty states
Functional requirements:

The product must provide an operating-context selector labelled “Delhi Metro Planning View”; it must be presented as a local view selector only and must not require login, create accounts, or enforce access control.
The product must allow creation and correction of stations. Each station must have one required name, and station names must be unique after trimming leading and trailing whitespace. A station cannot be removed while any timetable pattern references it.
The product must allow creation and correction of timetable patterns. Each pattern must own exactly one origin station, one destination station, one day type from Weekday, Weekend, or Holiday, one inclusive start time, one inclusive end time, and one baseline crowding level from Low, Medium, or High. Origin and destination must differ, start time must be earlier than end time, and no two patterns may have the same origin, destination, day type, and overlapping inclusive time ranges.
The product must allow creation and correction of public-holiday records. Each holiday record must own one calendar date and one required display name, and only one holiday record may exist for a date. A holiday date must classify that entire date as Holiday regardless of its weekday; a non-holiday Saturday or Sunday must classify as Weekend; every other non-holiday date must classify as Weekday.
The journey planner must require an origin station, a destination station, a calendar date, and a planned departure time. It must reject a request with identical origin and destination and visibly identify each missing or invalid input.
For a valid journey request, the product must derive the date’s day type, then match the single timetable pattern with the same origin, destination, derived day type, and an inclusive time range containing the planned departure time. When matched, the displayed predicted crowding must equal that pattern’s baseline crowding and the result must display the origin, destination, date, planned departure time, derived day type, and matched baseline crowding. When no pattern matches, it must display “No prediction available” and must not display a leave-earlier alert.
The product must create a saved prediction result only when a journey request has a matching timetable pattern. A saved result must retain the submitted journey facts, the day type derived at prediction time, the matched crowding level, and whether an alert was shown; later edits to stations, timetable patterns, or holidays must not alter already saved results.
The product must show an in-app alert only for a saved prediction whose matched crowding level is High. The alert text must include “Leave 20 minutes earlier” and must display a suggested departure time exactly 20 minutes before the submitted planned departure time, including when that time falls on the preceding calendar day. Low and Medium results must display no leave-earlier alert.
The product must provide a prediction-results list. By default, it must include all saved results ordered by journey date ascending and then planned departure time ascending; ties must be ordered by creation order ascending. It must support an optional filter of Low, Medium, or High that combines as an exact crowding-level match. With no saved results, or with no results matching the selected filter, it must show a visible no-results explanation.
The product must allow a user to correct a station, timetable pattern, or holiday record through its setup view. A rejected correction must leave the previously saved record unchanged and show the validation reason. Saved prediction results are historical and cannot be edited or deleted in the first version.
Core user journeys:

From the Delhi Metro Planning View, the user opens station setup, adds a station with a unique station name, and saves it; if the name is blank or duplicates an existing station name, saving is rejected with a visible validation message; otherwise the station appears in timetable setup.
From the Planning View, the user adds a timetable pattern by selecting an existing origin and destination station, a day type, a departure-time range, and a baseline crowding level; if origin and destination are identical or a required value is missing, the pattern is rejected; otherwise, it is available for prediction.
From the Planning View, the user opens holiday setup and adds a holiday date and name; if that date already has a holiday record, saving is rejected; otherwise, the date is classified as Holiday for predictions.
From the commuter journey planner, the user selects distinct origin and destination stations, a date, and a planned departure time and requests a prediction; the product determines the date’s day type, finds the applicable timetable pattern, and displays its predicted crowding level and the facts used. If no matching pattern exists, it displays “No prediction available” and no leave-earlier alert.
From the commuter journey planner, the user submits a journey whose matching timetable pattern has High baseline crowding; the product displays an in-app alert reading “Leave 20 minutes earlier,” shows the suggested departure time as 20 minutes before the entered time, and retains the entered planned time as the journey input.
From station or timetable setup, the user edits a saved record and submits valid changes; future predictions use the corrected record. If an edit would create a duplicate station name, duplicate holiday date, or invalid timetable pattern, the product keeps the prior saved record and shows the reason.
From the commuter planner, the user opens the results list without having run any predictions; the product shows an empty state explaining that no journey predictions have been created in the current local data.
From the commuter planner results list, the user filters saved prediction results by predicted crowding level; the product shows only results at that level, ordered by journey date then planned departure time ascending, or a visible no-results state when none match.
