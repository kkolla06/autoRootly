# autoRootly — Test Plan

Last refreshed: 2026-05-17 after analysis of `raw_ios_xml/ScreenRecording_05-17-2026 16-09-26_1.MP4`.

> See `ARCHITECTURE.md` for the suite shape and `raw_ios_xml/MISSING_XMLS.md` for the capture checklist.

## What changed after the recording

The walkthrough revealed several divergences from the previous plan. These are corrected throughout this file.

- **Alert statuses** are `Triggered` / `Acknowledged` / `Resolved` / `Deferred` — not `Active`/`Snoozed` as previously documented.
- **Alert detail bottom action is a slide gesture** (`Slide to ack` → `Slide to resolve` → `Escalate` button when Resolved), not a tap button.
- **List filter bar has 4 controls**: Sort (Most Recent / Most Urgent), Views (saved from Rootly Web), Status (multi-select), Ownership (single-select).
- **+ tab** opens a sheet: Create Incident / Create Alert / **Create Override** (the third option is new to us).
- **Alert + action menu** (state-conditional): Escalate / Add note / Mark as noise / Create Incident / Share. Escalate is hidden when the alert is Resolved because it becomes the primary action there.
- **Escalate is its own form**: "You're escalating the alert *X*. This will stop all in-progress paging and immediately notify the selected recipients."
- **Select Responders** is a shared sheet across Create Alert and Escalate: Escalation Policies / Services / Teams / People + search + Done.
- **Home flips to red "You've been paged"** with a View Alert button when the user has an active paging.
- **Create Incident has both Severity and Types dropdowns**; description field is labelled `Summary`.
- **Shifts** `0 Schedules` chip opens a **Select Schedules** modal (search + empty state).
- **Settings drawer** slides in from the right edge — distinct from the full Settings page.
- **Toasts**: `Incident created successfully`, `Manual page created successfully`, `You have escalated successfully`.

## How tests are organized

- One file per section below; mostly **extending existing files** rather than adding new ones.
- New files only for fundamentally new surfaces: `test_create_menu.py`, `test_paged_home.py`, `test_settings_drawer.py`.
- Style: **parametrized + multi-assert** to club similar cases into one test; a few **composite e2e** journeys for headline flows.
- Tests blocked by missing XML keep `@pytest.mark.skip` with a `raw_ios_xml/MISSING_XMLS.md (#N)` reason and unblock as XMLs land.

---

## Section 1 — Landing

| ID | Marker | What |
|---|---|---|
| TC-LAND-001 | smoke, p0 | Landing screen loads on cold launch (logo, tagline, Log in button visible). |
| TC-LAND-002 | smoke, p0 | Tapping Log in opens the embedded web form. |
| TC-LAND-003 | p1 | After Clear Cache & Data logout, Landing reappears. |

## Section 2 — Authentication

| ID | Marker | What |
|---|---|---|
| TC-AUTH-001 | smoke, p0 | All 8 elements of the web login form are present (email, password, Sign in, Remember me, SSO link, Google login, Slack login, Cancel). |
| TC-AUTH-002 | p1 | Cancel returns to Landing. |
| TC-AUTH-003 | smoke, p0 | Valid email + password reaches Home. |
| TC-AUTH-004 | p1 | Combined negative login (empty email, empty password, invalid format) followed by happy path — uses Cancel as form reset between attempts. |
| TC-AUTH-005 | p1 | Wrong password keeps user on the form. |
| TC-AUTH-006 | p2 | Show/hide password toggle flips field type. |
| TC-AUTH-007 | p2 | Remember me toggle changes state. |
| TC-AUTH-008..015 | p1/p2, skip | SSO / Google OAuth / Slack OAuth entry + happy-path + cancel — blocked on XML #23. |
| TC-AUTH-016..020 | p2/p3, skip | Create Account entry / valid / duplicate email / weak password / cancel — blocked on XML #23. |
| TC-AUTH-021 | smoke, p0 | Logout via Settings → Clear Cache & Data → confirm returns to Landing. |
| TC-AUTH-022 | p1 | Cancelling Clear Cache confirmation keeps user logged in. |
| TC-AUTH-023 | p2 | Log Out button transitions to Landing (acknowledging the known web-cache re-login bug). |
| TC-AUTH-024 | p1 | Re-login after Clear Cache & Data succeeds. |
| TC-AUTH-E01 | p3, edge | Email with leading/trailing whitespace — accepted or rejected, but never crashes. |
| TC-AUTH-E02 | p2, edge | Double-tap Sign in still results in a single successful login. |
| **TC-AUTH-E03** | p2, edge | **NEW** — iOS Face ID / Passwords autofill modal can be dismissed and manual entry still works. |
| **TC-AUTH-E04** | p3, edge | **NEW** — Cancel from the autofill modal → email field is still tappable + typeable. |

## Section 3 — Home dashboard

| ID | Marker | What |
|---|---|---|
| TC-HOME-001 | smoke, p0 | Home loads with: on-call status header, MY ACTIVITY widgets (Coverage Requests / Ongoing Alerts / Ongoing Incidents), MY PERFORMANCE cards (Time to ack / Time to resolve), and the bottom nav. Combined check. |
| TC-HOME-002 | p1 | On-call status text is one of `You're on-call` / `You're not on-call`. |
| TC-HOME-003 | p1 | Settings avatar opens Settings. |
| TC-HOME-004 | p2 | Home survives a scroll. |
| **TC-HOME-005** | smoke, p0 | **NEW** — Self-page in setup: Home shows `You've been paged` banner + alert preview card + View Alert button + Ongoing Alerts incremented. Combined assertion. |
| **TC-HOME-006** | p1 | **NEW** — View Alert button opens the alert just created (ID match). |
| **TC-HOME-007** | p1 | **NEW** — After resolving the alert, Home returns to normal state and Ongoing Alerts decrements. |

## Section 4 — Incidents lifecycle

### 4A — Incidents List

| ID | Marker | What |
|---|---|---|
| TC-INC-LIST-001 | smoke, p0 | Incidents list visible after navigating from bottom nav. |
| TC-INC-LIST-002 | p1 | At least one incident row with severity badge + title + status. |
| TC-INC-LIST-003 | p2 | **Filters combined** (parametrized over Status × Ownership): tap filter, confirm chip label updates, rows reflect selection. (Replaces the old "filter opens without crash" stub once XML #16 lands.) |
| TC-INC-LIST-004 | smoke, p0 | Tapping a row opens detail. |
| TC-INC-LIST-005 | p2 | Multiple scrolls don't crash the list. |

### 4B — Incident Detail

| ID | Marker | What |
|---|---|---|
| TC-INC-DET-001 | smoke, p0 | Detail header has severity badge, duration, and a status in the allowed set. |
| TC-INC-DET-003 | p1 | Details tab selected by default. |
| TC-INC-DET-005 | p1 | Alerts tab loads (and Details ↔ Alerts cycles without crashing). |
| TC-INC-DET-006 | p2 | `Add related alert` button visible. |
| TC-INC-DET-007 | p1 | Back returns to list. |
| **TC-INC-DET-012** | p1 | **NEW** — Incident state machine (after XML #17): Active → Acknowledge → Acknowledged → Resolve → Resolved, asserting badge + status text at each transition. Replaces 3 separate skipped tests. |

### 4C — Incident Creation

| ID | Marker | What |
|---|---|---|
| **TC-INC-CREATE-006** | p1 | **NEW (replaces 5)** — Parametrized over (severity ∈ SEV0/SEV2/SEV5) × (mark_as_private ∈ True/False). `+` → Create Incident → fill title+summary → set severity → toggle privacy → submit → `Incident created successfully` toast → row visible in list. |
| **TC-INC-CREATE-007** | p1 | **NEW (replaces 3)** — Validation combined: empty title → form stays open with inline error; Close → form dismissed + no row created; reopen → fields clean. |

## Section 5 — Alerts

### 5A — Alerts List

| ID | Marker | What |
|---|---|---|
| TC-ALERT-LIST-001 | smoke, p0 | Alerts list visible. |
| TC-ALERT-LIST-002 | p1 | At least one alert row. |
| TC-ALERT-LIST-004 | smoke, p0 | Tapping a row opens detail. |
| TC-ALERT-LIST-005 | p2 | List survives scroll. |
| **TC-ALERT-LIST-006** | p1 | **NEW** — Filters combined (parametrize over Status checkbox sets × Ownership radio): tap filter sheet → chip label updates → row count reflects selection. Replaces the weak "filter opens" test. (XML #14, #15.) |
| **TC-ALERT-LIST-007** | p2 | **NEW** — Sort + Views: parametrize over Sort ∈ {Most Recent, Most Urgent}; Views sheet shows empty-state copy `Choose a saved view from Rootly Web`. (XML #12, #13.) |

### 5B — Alert Detail

| ID | Marker | What |
|---|---|---|
| TC-ALERT-DET-001 | smoke, p0 | Header shows alert ID, severity, and status from VALID_STATUSES (now `Triggered`/`Acknowledged`/`Resolved`/`Deferred`). |
| TC-ALERT-DET-002 | p1 | Details tab is default + all 4 cards (Title / Responders / Labels / Related Incidents). |
| TC-ALERT-DET-004 | p1 | Tab cycle Details → Timeline → Payload → Details, no crash. |
| TC-ALERT-DET-005 | smoke, p0 | Escalate primary action is visible on Resolved alerts (button) — and the slide control replaces it in Triggered/Acknowledged. |
| TC-ALERT-DET-006 | p1 | Back returns to list. |
| **TC-ALERT-DET-008** | smoke, p0 | **NEW** — Alert state machine: self-page → Triggered + `Slide to ack` → slide_to_ack() → Acknowledged + `Slide to resolve` → slide_to_resolve() → Resolved + `Escalate` button. Single test asserts at every step. Uses W3C actions API (XML #5/6/7). |
| **TC-ALERT-DET-009** | p1 | **NEW** — + menu options conditional on state (parametrize over Triggered/Acknowledged/Resolved). Add note / Mark as noise / Create Incident / Share always present; Escalate present only when not Resolved. (XML #8.) |

### 5C — Alert Creation

| ID | Marker | What |
|---|---|---|
| **TC-ALERT-CREATE-006** | smoke, p0 | **NEW (replaces 4)** — Submit empty form → both validation errors visible (`Please specify who you want to notify.` + `Please enter a title.`). Then fill responder + urgency + title → submit → `Manual page created successfully` toast + row in list. (XML #3, #4.) |
| **TC-ALERT-CREATE-007** | p1 | **NEW** — Select Responders combined: open picker → search → expand category → select → Done → chip appears on form. |

### 5D — Alert Actions (+ menu and Escalate)

| ID | Marker | What |
|---|---|---|
| **TC-ALERT-ESC-001** | p1 | **NEW** — Escalate from + menu on a Triggered alert: form opens with alert title in copy → fill responder + urgency + note → Escalate → `You have escalated successfully` toast. (XML #9.) |
| **TC-ALERT-ESC-002** | p2 | **NEW** — Escalate from the primary action button on a Resolved alert: same form → submit → toast. |
| **TC-ALERT-ACT-001** | p2, skip | **NEW** — Add note flow (XML #21): empty rejected, real note appears on Timeline tab. |
| **TC-ALERT-ACT-002** | p2, skip | **NEW** — Mark as noise (XML #21): confirmation → alert relabeled / removed from default list. Observed behavior recorded. |
| **TC-ALERT-ACT-003** | p1, e2e | **NEW** — Create Incident from alert + menu (XML #21): toast + Related Incidents card on alert links to the new incident. |
| **TC-ALERT-ACT-004** | p3, skip | **NEW** — Share opens iOS share sheet; cancel returns to alert. |

## Section 6 — Shifts

| ID | Marker | What |
|---|---|---|
| TC-SHIFT-001 | smoke, p0 | Navigate to Shifts via bottom nav. |
| TC-SHIFT-002 | p1 | My shifts ↔ All shifts tab cycle. |
| TC-SHIFT-003 | p1 | Empty state copy shown when no shifts assigned. |
| TC-SHIFT-004 | p2 | KK avatar opens Settings. |
| **TC-SHIFT-005** | p1 | **NEW** — Select Schedules filter combined (XML #18): tap `0 Schedules` → modal opens → search bar visible → empty-state `No schedules to show` → X closes → list still rendered. |
| **TC-SHIFT-006** | p2, skip | **NEW** — Month picker (XML #19): `Shifts May ▾` opens picker → close → header unchanged. |

## Section 7 — Settings

| ID | Marker | What |
|---|---|---|
| TC-SET-001 | smoke, p0 | Settings opens from Home avatar. |
| TC-SET-002 | p1 | Profile card shows name + email + org + app version. Combined. |
| TC-SET-003 | p2 | All tappable rows open without crashing (combined sanity). |
| TC-SET-004 | p1 | On-Call Notifications row opens. |
| TC-SET-005 | p1 | Notification Settings row opens. |
| TC-SET-006 | p2 | Appearance row opens. |
| TC-SET-007 | p1 | Clear Cache & Data presents a confirmation. |
| TC-SET-008 | p1 | App version matches vX.Y.Z. |
| TC-SET-010 | p1 | Back returns to Home. |
| **TC-SET-011** | p2, skip | **NEW** — Settings right-edge drawer is distinct from full Settings (XML #20). Verify it does not navigate away from the underlying screen permanently. |

## Section 8 — Cross-screen navigation

| ID | Marker | What |
|---|---|---|
| TC-NAV-001 | smoke, p0 | Cycle Home → Alerts → Incidents → Shifts → Home; bottom nav present throughout. |
| TC-NAV-003 | p1 | Menu toggle opens a secondary menu without crashing. |
| TC-NAV-004 | p1 | Deep navigation back works (Incidents detail → list, Alerts detail → Timeline → back → list). |
| TC-NAV-005 | p2 | Settings avatar consistent across screens. |
| **TC-NAV-006** | smoke, p0 | **NEW** — `+` tab opens Create menu (Create Incident / Create Alert / Create Override visible) → X closes → bottom nav restored. (XML #1.) |

## Section 9 — E2E critical paths

| ID | Marker | What |
|---|---|---|
| TC-E2E-001 | smoke, p0 | Login → Alerts → open active alert. |
| TC-E2E-002 | smoke, p0 | Open alert → Escalate primary action → no crash. |
| TC-E2E-006 | p2 | Login → Home (read on-call status) → Shifts. |
| TC-E2E-007 | p1 | Full alert investigation: Details → Timeline → Payload → back to list. |
| TC-E2E-008 | smoke, p0 | Logout & re-login via Clear Cache & Data. |
| TC-E2E-009 | p1, skip | Google SSO end-to-end (XML #23). |
| TC-E2E-010 | p1, skip | Slack SSO end-to-end (XML #23). |
| **TC-E2E-011** | smoke, p0 | **NEW — headline test**: login → `+` → Create Alert (self responder) → toast → Home red `You've been paged` + View Alert → tap → Alert Detail Triggered → `slide_to_ack` → Acknowledged → `slide_to_resolve` → Resolved → Home banner gone. Single composite journey. |
| **TC-E2E-012** | p1 | **NEW** — Escalation journey: open Triggered alert → + → Escalate → fill → toast → observe (don't assert) post-state on Timeline tab; ack → resolve still work afterwards. |
| **TC-E2E-013** | p1 | **NEW** — Create incident from alert: open alert → + → Create Incident → submit → toast → switch to Incidents tab → new incident at top → back to alert → Related Incidents card shows link. |

## Section 10 — Edge cases

| ID | Marker | What |
|---|---|---|
| TC-EDGE-001 | p2 | Rapid tab switching doesn't crash. |
| TC-EDGE-002 | p1, skip | Double-tap submit produces single resource (XML #1). |
| TC-EDGE-003 | p2, skip | Reopen create form shows empty fields (XML #1). |
| TC-EDGE-004 | p1 | Cold start after terminate reaches Home or Landing. |
| TC-EDGE-005 | p2 | Backgrounding/foregrounding preserves state. |
| TC-EDGE-006 | p2 | Resolved alert still allows Escalate (current behavior documented). |
| TC-EDGE-008 | p3 | List survives 5 consecutive scrolls. |
| TC-EDGE-009 | p3 | Detail → back → list still renders. |
| **TC-EDGE-010** | p2 | **NEW** — Sheet dismissal: any bottom sheet (Sort/Views/Status/Ownership/Select Responders/Select Schedules/Create menu/Alert +) closes via outside-tap or X without crashing. Parametrized over sheet openers. |
| **TC-EDGE-011** | p2 | **NEW** — Toast lifecycle: success toast visible ≤10s, disappears on its own, doesn't block the next action. Parametrized over toast texts. |
| **TC-EDGE-012** | p3 | **NEW** — Long inputs: 200+ char alert title / 2000+ char incident summary → submit succeeds OR clear error; app doesn't freeze. |
| **TC-EDGE-013** | p3 | **NEW** — Emoji + special chars in title round-trip through the row. |
| **TC-EDGE-014** | p2 | **NEW** — Rapid double-tap on Slide-to-ack handle results in one ack, not a double-toggle. |
| **TC-EDGE-015** | p3 | **NEW** — Cancel mid-slide: drag partway and release → status stays Triggered. |
| **TC-EDGE-016** | p3 | **NEW** — Background during create form preserves field contents on foreground. |
| **TC-EDGE-017** | p2 | **NEW** — Filter combinations across Status × Ownership produce expected row sets (parametrized). |
| **TC-EDGE-018** | p1 | **NEW** — Resolved alert + menu = {Add note, Mark as noise, Create Incident, Share}; Escalate hidden. Parametrized counterpart of TC-ALERT-DET-009. |

---

## Marker quick-reference

- `pytest -m smoke` — every TC-* with `smoke` (and `p0`) marker; minimum CI gate.
- `pytest -m "alerts and p1"` — alert state machine, +menu, escalate flows.
- `pytest -m edge` — boundary tests; may legitimately skip when XML still missing.
- `pytest -m e2e` — composite journeys, including TC-E2E-011 (the headline).

## Implementation order (after plan + XML landing)

1. **Fix + relabel** (no new tests): rename `VALID_STATUSES`, fix `Summary` label, add slide + toast helpers in `BasePage`.
2. **POMs for surfaces with XML available**: `create_menu`, `select_responders`, `select_schedules`, `alert_escalate_page`, split `alert_detail_page`.
3. **Headline tests**: TC-E2E-011 + TC-ALERT-DET-008 + TC-HOME-005..007 + TC-ALERT-CREATE-006.
4. **Parametrized filter + edge tests**.
5. **Unblock deferred actions** as XMLs land: Add note / Mark as noise / Share / Create Override / Settings drawer.
