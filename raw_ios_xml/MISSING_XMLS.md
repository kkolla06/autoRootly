# Missing XML Captures

Tests blocked by missing XML are `@pytest.mark.skip` with a reason pointing back here. Once a screen's XML lands, update the corresponding page object's `TODO` locator and unskip the dependent tests.

Refreshed 2026-05-17 after analysis of the walkthrough recording.

## How to capture

1. Open Appium Inspector against the running session.
2. Navigate to the screen / state listed below.
3. Save page source into `raw_ios_xml/` with a descriptive name (e.g. `rootly-alert_detail_triggered.xml`).
4. Update the page object: replace `TODO` placeholder locator(s) with the real accessibility id, then unskip the test(s) in the **Unblocks** column.

## Capture checklist (in execution order — one Inspector session)

| # | Screen / State | Suggested filename | Why we need it | Unblocks |
|---|---|---|---|---|
| 1 | ~~**`+` tab sheet**~~ | ~~`rootly-create_menu.xml`~~ | **Captured** as `rootly-home-with-create.xml`. TC-NAV-006 unskipped. TC-INC-CREATE-*, TC-ALERT-CREATE-*, TC-EDGE-002/003/012/013/016 still skipped pending their own form locators. | — |
| 2 | **Create Incident — Severity picker open** | `rootly-incident_create_severity_open.xml` | Picker options (SEV0..SEV5) | TC-INC-CREATE-006 |
| 3 | **Create Incident — Types picker open** | `rootly-incident_create_types_open.xml` | Picker options | TC-INC-CREATE-006 |
| 4 | ~~**Create Alert — Urgency picker open**~~ | ~~`rootly-alert_create_urgency_open.xml`~~ | **Captured**. Header "Select Urgency"; options High (default selected), Medium, Low — all XCUIElementTypeButton. UrgencySheet class added to alert_escalate_page.py. TC-ALERT-CREATE-006 locators confirmed. | — |
| 5 | ~~**Select Responders sheet**~~ | ~~`rootly-select_responders_*.xml`~~ | **Captured** as `rootly-create-select_responders.xml`. All section locators confirmed. Items are XCUIElementTypeSwitch with enabled=false — runtime tap behaviour TBD. TC-ALERT-CREATE-006/007 unskipped; paged_alert fixture unblocked. | — |
| 6 | ~~**Alert detail — Triggered state**~~ | ~~`rootly-alert_detail_triggered.xml`~~ | **Captured**. slide_button confirmed (StaticText, name="slide_button", label="Slide to ack"). Action menu adds Resolve + Escalate. TC-ALERT-DET-008 locators fully confirmed. | — |
| 7 | ~~**Alert detail — Acknowledged state**~~ | ~~`rootly-alert_detail_acknowledged.xml`~~ | **Captured**. slide_button confirmed (Image, name="slide_button", label="Slide to resolve"). Action menu has Escalate but NOT Resolve. TC-ALERT-DET-008 locators fully confirmed. | — |
| 8 | ~~**Alert detail — Resolved state**~~ | ~~`rootly-alert_detail_resolved.xml`~~ | **Captured** as `rootly-alert_detail_resolved.xml`. All locators confirmed (tabs, cards, header predicates, ESCALATE_BUTTON, ACTION_MENU_BUTTON). TC-ALERT-DET-005/008, TC-ALERT-ESC-002 unblocked. | — |
| 9 | ~~**Alert detail `+` action menu**~~ | ~~`rootly-alert_action_menu_resolved.xml`~~ | **Captured** for all 3 states. All option locators confirmed; Escalate absent on Resolved confirmed. CLOSE_BUTTON confirmed in escalate form (not in action menu). TC-ALERT-DET-009 unskipped. | — |
| 10 | ~~**Escalate form + "Escalate to" sheet**~~ | ~~`rootly-alert_escalate_to_sheet.xml`~~, `rootly-alert_escalate_form.xml` | **Captured**. Two-step flow confirmed: Escalate -> AlertEscalateToSheet (Confirm) -> AlertEscalatePage. All locators confirmed (CLOSE_BUTTON, NOTIFY_DROPDOWN predicate, URGENCY_DROPDOWN, NOTE_FIELD, SUBMIT_CONTAINER="manual_page_create_button"). TC-ALERT-ESC-001/002, TC-E2E-012 unblocked. | — |
| 11 | **Success toasts** — capture during each of `Incident created successfully` / `Manual page created successfully` / `You have escalated successfully` | `rootly-toast_*.xml` | Locator strategy + lifecycle | TC-ALERT-CREATE-006, TC-INC-CREATE-006, TC-ALERT-ESC-001, TC-EDGE-011 |
| 12 | **Home — "You've been paged" red state** | `rootly-home_paged.xml` | Banner + View Alert + alert preview card locators | TC-HOME-005/006/007, TC-E2E-011 |
| 13 | ~~**Alerts list — Sort sheet open**~~ | ~~`rootly-alerts_sort_sheet.xml`~~ | **Captured** as `rootly-alerts_sort_sheet.xml`. Locators confirmed. TC-ALERT-LIST-007 unblocked pending #14. | — |
| 14 | ~~**Alerts list — Views sheet open**~~ | — | **Won't test** — no saved views in the demo account; feature not in scope. TC-ALERT-LIST-007 Views assertions dropped. | — |
| 15 | ~~**Alerts list — Status sheet open**~~ | ~~`rootly-alerts_status_sheet.xml`~~ | **Captured** as `rootly-alerts_status_sheet.xml`. Locators confirmed. TC-ALERT-LIST-006 unblocked pending #16. | — |
| 16 | ~~**Alerts list — Ownership sheet open**~~ | ~~`rootly-alerts_ownership_sheet.xml`~~ | **Captured** as `rootly-alerts_ownership_sheet.xml`. Locators confirmed. TC-ALERT-LIST-006 fully unblocked. | — |
| 17 | **Incidents list — Status sheet open + Ownership sheet open** | `rootly-incidents_status_sheet.xml`, `rootly-incidents_ownership_sheet.xml` | Confirm they mirror Alerts | TC-INC-LIST-003 |
| 18 | **Incident detail — Active state with Acknowledge button** + **Acknowledged with Resolve button** | `rootly-incident_detail_active.xml`, `rootly-incident_detail_acknowledged.xml` | Acknowledge / Resolve button locators | TC-INC-DET-012 |
| 19 | **Shifts — Select Schedules modal open** | `rootly-shifts_select_schedules.xml` | Search + empty-state | TC-SHIFT-005 |
| 20 | **Shifts — month picker open** | `rootly-shifts_month_picker.xml` | Month nav locators | TC-SHIFT-006 |
| 21 | **Settings right-edge drawer** | `rootly-settings_drawer.xml` | Distinct surface from full Settings | TC-SET-011 |
| 22a | ~~**Alert detail — Add note sheet**~~ | ~~`rootly-alert_addnote.xml`~~ | **Captured**. NOTE_FIELD="Anything you want to add to the alert?" (TextField), SUBMIT_CONTAINER="note_bottom_sheet_add_note_button", SUBMIT_BUTTON="Add note". No close button — dismiss via swipe-down. TC-ALERT-ACT-001 unskipped; note verified on Timeline tab. | — |
| 22b | **Alert detail — Mark as noise sheet** | `rootly-alert_marknoise.xml` | Post-noise state confirmed (`rootly-alert_detail_noise.xml`): Noise badge (name="Noise") appears alongside Resolved chip. Still need the sheet that appears when you tap "Mark as noise". TC-ALERT-ACT-002 assertion ready; unskip once sheet XML captured. | TC-ALERT-ACT-002 |
| 22c | **Alert detail — Share sheet** | `rootly-alert_share.xml` | iOS share sheet | TC-ALERT-ACT-004 |
| 23 | **Create Override** form | `rootly-create_override.xml` | Currently deferred entirely; capture when convenient | (deferred) |
| 24 | **iOS Face ID / Passwords autofill modal** (appears at top of login form) | `rootly-login_autofill_modal.xml` | New finding from recording | TC-AUTH-E03/E04 |
| 25 | **SSO subdomain screen** | `rootly-login_sso_subdomain.xml` | Carried over | TC-AUTH-008/009, TC-E2E-009/010 |
| 26 | **Google OAuth sheet** | `rootly-login_google_oauth.xml` | Carried over | TC-AUTH-010..012, TC-E2E-009 |
| 27 | **Slack OAuth sheet** | `rootly-login_slack_oauth.xml` | Carried over | TC-AUTH-013..015, TC-E2E-010 |
| 28 | **Create Account form + entry link** | `rootly-create_account_*.xml` | Carried over | TC-AUTH-016..020 |

## Notes on current XML

- `rootly-login_web.xml` shows the embedded WebView form. Email + password fields have empty `name`/`label` and are located by predicate on `type`. Google and Slack links at x=88 and x=158 also have no `name` — located via class-chain index. Replace both with accessibility IDs once available.
- `rootly-incident_details.xml` was captured in a Resolved state, so Acknowledge / Resolve buttons aren't visible. **Capture #18 supersedes this** — need both Active and Acknowledged states.
- `rootly-alert_details.xml` was likewise captured in Resolved state. Captures #6 and #7 supersede this.
- `rootly-shifts.xml` was captured with `0 Schedules` (empty state). A capture with at least one shift would help verify the populated layout — not blocking, but useful.

## Status quick-reference

Alert statuses (from the recording): **`Triggered` / `Acknowledged` / `Resolved` / `Deferred`** — replaces the older `Active`/`Snoozed` documentation. Each surfaces both as a colored dot (red / orange / green / blue) on list rows and as a labelled chip on detail.

Incident statuses (provisional, awaiting #18 confirmation): `Active` / `Mitigated` / `Resolved`. Page object will be updated after capture.
