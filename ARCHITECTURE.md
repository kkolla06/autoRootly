# autoRootly — Architecture

Last updated: 2026-05-17 (after walkthrough recording analysis)

## 1. Stack

| Layer | Choice |
|---|---|
| Test runner | `pytest` (+ `pytest-html` for reports) |
| Driver | Appium 5.x Python Client over XCUITest |
| App under test | Rootly iOS native (bundle `APP_BUNDLE_ID`) + embedded WebView for auth |
| Pattern | Page Object Model (one class per screen / modal) |
| Config | `python-dotenv` → `.env` (credentials, device UDID, bundle id) |
| CI hook | Local for now; report at `output/report.html` + screenshots in `assets/` |

## 2. Directory layout

```
autoRootly/
├─ ARCHITECTURE.md          # this file
├─ PLAN.md                  # test plan + matrix
├─ README.md
├─ requirements.txt
├─ pytest.ini               # markers + log config
├─ conftest.py              # session driver + per-test login + cold-start reset
├─ .env                     # ROOTLY_TEST_EMAIL / _PASSWORD / DEVICE_* / APP_BUNDLE_ID
│
├─ config/
│  └─ capabilities.py       # XCUITest options
│
├─ pages/                   # one POM file per screen / modal
│  ├─ base_page.py          # find / tap / type / scroll / locator helpers
│  ├─ landing_page.py
│  ├─ login_page.py         # web form inside WebView
│  ├─ home_page.py          # default + "You've been paged" variant
│  ├─ shifts_page.py
│  ├─ settings_page.py      # full Settings screen
│  ├─ settings_drawer.py    # NEW — right-edge slide-out drawer (different from full Settings)
│  ├─ create_menu.py        # NEW — bottom sheet opened from the + tab
│  ├─ select_responders.py  # NEW — bottom sheet shared by Create Alert + Escalate
│  ├─ select_schedules.py   # NEW — bottom sheet opened from "0 Schedules" on Shifts
│  ├─ severity_picker.py    # NEW — for Create Incident
│  ├─ types_picker.py       # NEW — for Create Incident
│  ├─ urgency_picker.py     # NEW — for Create Alert + Escalate
│  │
│  ├─ alerts/
│  │  ├─ alerts_page.py            # list + sort/views/status/ownership filter bar
│  │  ├─ alert_detail_page.py      # NEW (currently merged into alerts_page) — Details/Timeline/Payload + slide-to-act
│  │  ├─ alert_create_page.py      # Create Alert form
│  │  ├─ alert_escalate_page.py    # NEW — Escalate form (own modal)
│  │  ├─ alert_action_menu.py      # NEW — the + sheet on alert detail (Escalate/Add note/Mark as noise/Create Incident/Share)
│  │  └─ alert_sort_filter.py      # NEW — Sort + Views + Status + Ownership sheets
│  │
│  └─ incidents/
│     ├─ incident_list_page.py     # list + same filter bar shape as alerts
│     ├─ incident_detail_page.py
│     ├─ create_incident_page.py
│     └─ incident_sort_filter.py   # NEW
│
├─ tests/                   # one file per Section in PLAN.md (mirrors markers)
│  ├─ test_landing.py
│  ├─ test_login.py
│  ├─ test_home.py
│  ├─ test_incident_lifecycle.py
│  ├─ test_alerts.py
│  ├─ test_alerts_filters.py       # NEW — sort/views/status/ownership combos
│  ├─ test_alert_actions.py        # NEW — slide-to-ack, slide-to-resolve, escalate from + menu, add note, mark as noise
│  ├─ test_incident_filters.py     # NEW
│  ├─ test_shifts.py
│  ├─ test_settings.py
│  ├─ test_settings_drawer.py      # NEW
│  ├─ test_create_menu.py          # NEW
│  ├─ test_paged_home.py           # NEW — "You've been paged" state
│  ├─ test_navigation.py
│  ├─ test_e2e.py
│  └─ test_edge_cases.py
│
├─ utils/
│  └─ helpers.py            # autouse screenshot-on-failure hook
│
├─ raw_ios_xml/             # captured page sources + MISSING_XMLS.md
│  └─ ScreenRecording_05-17-2026 16-09-26_1.MP4   # the walkthrough recording
│
├─ output/                  # pytest-html report
└─ assets/                  # FAILED_*.png screenshots (gitignored)
```

## 3. Driver lifecycle

- `driver` fixture is **session-scoped** → one Appium session for the whole run.
- `noReset=True` keeps the keychain so we don't re-login on every test.
- `login` fixture is **function-scoped**:
  - If the Home indicator (`ongoing_incidents`) is visible → reuse session.
  - Else → drive Landing → Log in → web form → Sign in.
  - On teardown: `terminate_app` + `activate_app` so the next test starts from a known screen (Home if session preserved, Landing if cleared).
- Failure screenshots are autosaved by `utils/helpers.py` → `assets/FAILED_<test_name>.png`.

## 4. App information architecture (from walkthrough recording)

```
Cold launch
└── Landing (3D alert card stack + tagline + "Log in")
    └── Web login form (rootly.com WebView)
        ├── Google login link  ─────────┐
        ├── Slack login link    ────────┤  (each opens its own OAuth sheet)
        ├── SSO link            ────────┘  (opens subdomain entry)
        └── Email + Password → Sign in
            │   (iOS Face ID Passwords prompt may appear here first)
            └── Home dashboard
                ├── Header: on-call status banner (normal black OR RED "You've been paged")
                ├── MY ACTIVITY: Coverage Requests, Ongoing Alerts, Ongoing Incidents (tappable)
                ├── MY PERFORMANCE: Time to ack, Time to resolve
                ├── Settings avatar (top-right, opens full Settings screen)
                │
                └── Bottom nav (5 items)
                    ├── Home tab
                    ├── Alerts tab
                    │   └── Alerts list
                    │       ├── Sort sheet     (Most Recent / Most Urgent)
                    │       ├── Views sheet    (saved views from Rootly Web; empty by default)
                    │       ├── Status sheet   (Triggered / Acknowledged / Resolved / Deferred — multi-select)
                    │       ├── Ownership sheet(All alerts / My Team's alerts / My alerts — single-select)
                    │       └── Alert row → Alert Detail
                    │           ├── Tabs: Details / Timeline / Payload
                    │           ├── Cards: Services, Teams, Title, Responders, Labels, Related Incidents
                    │           ├── Status label (Triggered / Acknowledged / Resolved)
                    │           ├── Bottom action (state-dependent):
                    │           │   • Triggered    → "Slide to ack"
                    │           │   • Acknowledged → "Slide to resolve"
                    │           │   • Resolved     → "Escalate" button
                    │           └── + menu (alert action sheet):
                    │               • Escalate     (hidden when alert is Resolved)
                    │               • Add note
                    │               • Mark as noise
                    │               • Create Incident
                    │               • Share
                    │               • X (close)
                    │
                    ├── Incidents tab (flame icon)
                    │   └── Incidents list — same filter-bar shape as Alerts
                    │       └── Incident Detail
                    │           ├── Tabs: Details / Alerts
                    │           ├── Severity badge (SEV0..SEV5), duration, status
                    │           ├── Acknowledge / Resolve actions (TBD — XML still missing)
                    │           └── "Add related alert" button
                    │
                    ├── Shifts tab
                    │   └── Shifts screen
                    │       ├── "Shifts May" calendar dropdown (month picker — XML missing)
                    │       ├── "0 Schedules" chip → Select Schedules modal (search + empty state)
                    │       ├── Tabs: My shifts / All shifts
                    │       └── Empty state copy when no shifts
                    │
                    └── + tab (creation entry point — bottom sheet)
                        ├── Create Incident → Create Incident form
                        │   ├── Title *, Summary, Severity ▼, Types ▼, Mark as Private toggle
                        │   └── Submit → "Incident created successfully" toast → list updates
                        ├── Create Alert    → Create Alert form
                        │   ├── Who to notify * (opens Select Responders), Urgency * ▼, Title *, Description
                        │   └── Submit → "Manual page created successfully" toast → list updates
                        │       (Home flips to "You've been paged" if you become a recipient)
                        ├── Create Override → ??? form (XML missing, MUST capture)
                        └── X (close)

Settings page (full screen — opened from avatar)
├── Back button
├── Profile card: avatar, Name, Email, Org chip
├── Members, On-Call Notifications, Appearance (System), Language (English)
├── Email Support
└── About (vX.Y.Z), Troubleshooting, Notification Settings, Clear Cache & Data, (Update Contact Card), (Log Out)

Settings drawer (right-edge slide-in — different from full Settings)
└── Distinct surface seen in recording overlaying the Shifts screen; need XML to confirm scope.
```

## 5. Locator strategy

We prefer in this order:

1. **`accessibility id`** — most stable.
2. **`-ios predicate string`** — when name/label is dynamic or we need a regex/set match.
3. **`-ios class chain`** — last resort for anonymous WebView nodes (Google/Slack login links, password show toggle).
4. Never rely on visual position or XPath that walks the whole tree.

Page objects expose tuple locators as class constants and methods that combine them into intent ("fill_title", "submit"). Tests speak in intents, not locators.

## 6. Markers (pytest.ini)

| Marker | Meaning |
|---|---|
| `smoke` | P0 — must pass on every CI run |
| `landing` `login` `home` `incident` `alerts` `shifts` `settings` `navigation` `e2e` `edge` | scope tags |
| `p0` `p1` `p2` `p3` | priority — p0 are smoke, p3 are edge/boundary |

Run e.g. `pytest -m "smoke and not skip"` or `pytest -m "alerts and p1"`.

## 7. Open architectural questions

1. **Settings drawer vs. Settings page** — are they the same data with different presentations, or distinct surfaces? The recording shows both. Treat as separate POMs until proven equivalent.
2. **"Views" filter** — pulls saved views from Rootly Web. Should we exercise this against a stub view, or treat it as integration-tested only? Currently unfilled in the demo account.
3. **Slide-to-ack / Slide-to-resolve** — Appium does not have a native "slide a button" gesture. We'll need a `mobile: dragFromToForDuration` helper in `base_page.py` that takes the slider's start and end coordinates. Documented as a TODO in the page object.
4. **Toast verification** — the success toasts ("Incident created successfully", "Manual page created successfully", "You have escalated successfully") are short-lived and rendered above the bottom nav. We need a fast `wait_for_visible(toast, timeout=5)` + `wait_for_gone(toast, timeout=10)` pattern.
5. **Paged-home** — the red "You've been paged" home state is conditional. Should it be reproduced by creating a self-page in setup, or asserted opportunistically when the precondition naturally exists?
