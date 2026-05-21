# autoRootly

End-to-end iOS automation suite for the Rootly app — built with Appium + pytest. Covers auth, home, alerts, incidents, shifts, settings and headline e2e journeys, plus a manual bug report.

- **Github repo**: https://github.com/kkolla06/autoRootly
- **Bug Report**: https://docs.google.com/document/d/1syRAMvD9rEMA4RRxix-TliYbRv0k75VAg8zpBQiGc4M
- **Demo**: https://drive.google.com/file/d/1DFWA3VX2marKM9jqlAEgOaPfblh5rNlB

## What it covers

- **Auth**: landing → web login (email/password, Google, Slack, SSO), logout, re-login.
- **Home**: on-call status, My Activity widgets, "You've been paged" red state.
- **Alerts**: list + filters (Sort / Views / Status / Ownership), detail with state machine (Triggered → Acknowledged → Resolved via slide gestures), + action menu (Escalate / Add note / Mark as noise / Create Incident / Share), create + escalate flows.
- **Incidents**: list + filters, detail, create form with Severity / Types / privacy.
- **Shifts**: My / All tabs, Select Schedules modal.
- **Settings**: full page + right-edge drawer.
- **E2E headlines**: self-page → ack → resolve, escalate journey, create incident from alert.
