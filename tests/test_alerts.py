"""Alert tests — Section 5 of PLAN.md.

Designed for a clean-slate run (0 alerts assumed at start).

The first two tests create the two named alerts. Every subsequent test
navigates to one of them by title — no fixtures, no hidden setup.

  ALERT_A ("AutoTest-A") — created in test 1, stays Triggered.
    Used by: detail/tab tests, Triggered action-menu, escalate-from-menu.
  ALERT_B ("AutoTest-B") — created in test 2, driven through state machine.
    Used by: state-machine, Resolved action-menu, escalate-primary, noise.

Run the full module in declaration order. Individual tests further down
the file assume the creation tests have already run in the same session.
"""
import time
import pytest
from pages.home_page import HomePage
from pages.alerts.alerts_page import AlertsPage
from pages.alerts.alert_detail_page import AlertDetailPage
from pages.alerts.alert_create_page import AlertCreatePage
from pages.alerts.alert_escalate_page import AlertEscalatePage, AlertEscalateToSheet
from pages.alerts.alert_add_note import AlertAddNoteSheet
from pages.alerts.alert_action_menu import AlertActionMenu
from pages.alerts.alert_sort_filter import (
    AlertSortSheet,
    AlertStatusSheet,
    AlertOwnershipSheet,
)
from pages.create_menu import CreateMenu
from pages.incidents.create_incident_page import CreateIncidentPage
from pages.select_responders import SelectResponders

# Known alert titles — module constants referenced by all tests below.
ALERT_A = "DEMO-autoRootly-A"  # stays Triggered throughout
ALERT_B = "DEMO-autoRootly-B"  # driven through full state machine


def _create_alert(login, title):
    """Open the Create Alert form, add Kaushik as responder, set title, submit."""
    home = HomePage(login)
    home.open_menu()
    CreateMenu(login).tap_create_alert()
    form = AlertCreatePage(login)
    form.wait_for_visible(form.SUBMIT_BUTTON)
    form.open_responder_picker()
    picker = SelectResponders(login)
    picker.wait_for_visible(picker.SEARCH_FIELD)  # sheet open + list ready
    picker.expand_category("People")
    picker.select("Kaushik Kolla")
    picker.done()
    form.fill_title(title)
    form.submit()
    form.wait_for_toast("Manual page created successfully", timeout=15)
    return form


# ====================================================================== #
# 5C — Alert Creation                                                     #
# Tests 1-3: prove the create UX and produce the two named alerts.       #
# ====================================================================== #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.alerts
def test_create_alert_a(login):
    """TC-ALERT-CREATE-006 — Creates ALERT_A in Triggered state.

    This is the first required setup test — all subsequent tests navigate
    to ALERT_A by title.
    """
    _create_alert(login, ALERT_A)


@pytest.mark.p2
@pytest.mark.alerts
def test_create_alert_validation(login):
    """TC-ALERT-CREATE-006b — empty submit shows title + notify inline errors."""
    home = HomePage(login)
    home.open_menu()
    CreateMenu(login).tap_create_alert()
    form = AlertCreatePage(login)
    form.wait_for_visible(form.SUBMIT_BUTTON)
    form.submit()
    assert form.title_error_visible(), "Title validation error missing"
    assert form.notify_error_visible(), "Responder validation error missing"


@pytest.mark.p0
@pytest.mark.alerts
def test_create_alert_b(login):
    """Creates ALERT_B — will be driven through the state machine later."""
    _create_alert(login, ALERT_B)


# ====================================================================== #
# 5A — Alerts List                                                        #
# Alert A and B are both in Triggered state from here on.                #
# ====================================================================== #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.alerts
def test_alerts_list_loads(login):
    """TC-ALERT-LIST-001/002 — list visible and contains at least one row."""
    HomePage(login).go_to_alerts()
    alerts = AlertsPage(login)

    alerts.tap_status_filter()
    sheet = AlertStatusSheet(login)
    sheet.toggle("Triggered")
    sheet.dismiss()
    assert not alerts.is_visible(alerts.STATUS_FILTER_VALUE, timeout=3), \
        "STATUS_FILTER_VALUE should be gone when Triggered filter is active"

    assert alerts.is_alerts_list_visible(), "Alerts list not visible"
    assert alerts.has_any_alert(), "No alert rows visible"

    alerts.tap_status_filter()
    sheet.toggle("Triggered")
    sheet.dismiss()
    assert alerts.is_visible(alerts.STATUS_FILTER_VALUE, timeout=5), \
        "STATUS_FILTER_VALUE should reappear once filter is cleared"


@pytest.mark.p2
@pytest.mark.alerts
@pytest.mark.parametrize("sort_option", ["Most Recent", "Most Urgent"])
def test_alerts_sort(login, sort_option):
    """TC-ALERT-LIST-007 — Sort sheet opens, selection persists, list renders."""
    HomePage(login).go_to_alerts()
    alerts = AlertsPage(login)
    alerts.tap_sort()
    sort_sheet = AlertSortSheet(login)
    assert sort_sheet.is_visible(), "Sort sheet did not open"
    sort_sheet.select(sort_option)
    sort_sheet.dismiss()
    assert alerts.is_alerts_list_visible(), "Alerts list lost after Sort selection"


@pytest.mark.p2
@pytest.mark.alerts
def test_alerts_list_scrollable(login):
    """TC-ALERT-LIST-005."""
    HomePage(login).go_to_alerts()
    AlertsPage(login).scroll_down()


# ====================================================================== #
# 5B — Alert Detail: Alert A (Triggered state)                           #
# ====================================================================== #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.alerts
def test_alert_a_detail_header(login):
    """TC-ALERT-DET-001 — Alert A header: ID present, severity badge, status=Triggered."""
    HomePage(login).go_to_alerts()
    AlertsPage(login).open_alert_by_title(ALERT_A)
    detail = AlertDetailPage(login)
    assert detail.is_visible(detail.ALERT_ID, timeout=10), "Alert ID missing in header"
    assert detail.has_severity_badge(), "Severity badge missing"
    assert detail.get_status() == "Triggered", "Alert A should be Triggered"


@pytest.mark.p1
@pytest.mark.alerts
def test_alert_a_tabs_and_cards(login):
    """TC-ALERT-DET-002/003/004 — Details tab default, four cards, tabs cycle."""
    HomePage(login).go_to_alerts()
    AlertsPage(login).open_alert_by_title(ALERT_A)
    detail = AlertDetailPage(login)

    assert detail.is_detail_visible(), "Details tab should be active by default"
    assert detail.all_cards_visible(), (
        "One of the four Detail cards is missing "
        "(title / responders / labels / related_incidents)"
    )
    detail.tap_timeline_tab()
    assert detail.is_visible(detail.TIMELINE_TAB, timeout=5)
    detail.tap_payload_tab()
    assert detail.is_visible(detail.PAYLOAD_TAB, timeout=5)
    detail.tap_details_tab()
    assert detail.is_detail_visible(), "Returning to Details tab failed"


# ====================================================================== #
# 5D — Action menu: Alert A (Triggered state)                            #
# ====================================================================== #


@pytest.mark.p1
@pytest.mark.alerts
def test_alert_a_action_menu_options(login):
    """TC-ALERT-DET-009 (Triggered) — + menu shows Resolve + Escalate + always-present."""
    HomePage(login).go_to_alerts()
    AlertsPage(login).open_alert_by_title(ALERT_A)
    AlertDetailPage(login).open_action_menu()
    menu = AlertActionMenu(login)
    assert menu.is_visible_option("Add note"), "+ menu missing Add note"
    assert menu.is_visible_option("Mark as noise"), "+ menu missing Mark as noise"
    assert menu.is_visible_option("Create Incident"), "+ menu missing Create Incident"
    assert menu.is_visible_option("Share"), "+ menu missing Share"
    assert menu.is_visible_option("Escalate"), "Escalate should be visible in Triggered action menu"
    assert menu.is_visible_option("Resolve"), "Resolve should be visible in Triggered action menu"


# ====================================================================== #
# 5B — State machine: Alert B (Triggered -> Acknowledged -> Resolved)    #
# Acknowledged action-menu is checked inline — only window to do so.     #
# ====================================================================== #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.alerts
def test_alert_b_state_machine(login):
    """TC-ALERT-DET-008 — Alert B: Triggered -> slide-to-ack (verify Acked menu) ->
    slide-to-resolve -> Escalate button appears.
    """
    driver = login
    HomePage(driver).go_to_alerts()
    AlertsPage(driver).open_alert_by_title(ALERT_B)
    detail = AlertDetailPage(driver)

    assert detail.get_status() == "Triggered", "Alert B should start Triggered"
    assert detail.is_visible(detail.SLIDE_TO_ACK, timeout=5), "Slide to ack not visible"

    detail.slide_to_ack()
    time.sleep(2)
    detail.wait_for_visible(("accessibility id", "Acknowledged"), timeout=10)
    assert detail.get_status() == "Acknowledged"

    # Acknowledged action menu — only natural opportunity in the suite
    detail.open_action_menu()
    acked_menu = AlertActionMenu(driver)
    assert acked_menu.is_visible_option("Escalate"), "Escalate missing in Acknowledged menu"
    assert not acked_menu.is_visible_option("Resolve"), "Resolve should be absent in Acknowledged menu"
    # detail.dismiss_sheet()  # swipe down to close before proceeding
    detail.dismiss_sheet_alert_ack_menu()
    detail.wait_for_visible(detail.SLIDE_TO_RESOLVE, timeout=8)  # sheet gone, resolve slider settled

    detail.slide_to_resolve()
    detail.wait_for_visible(("accessibility id", "Resolved"), timeout=10)
    assert detail.get_status() == "Resolved"


# ====================================================================== #
# 5B/D — Resolved-state tests: Alert B                                   #
# Alert B is Resolved from here on.                                      #
# ====================================================================== #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.alerts
def test_escalate_button_visible_on_resolved(login):
    """TC-ALERT-DET-005 — Alert B is Resolved; Escalate is the primary action."""
    HomePage(login).go_to_alerts()
    AlertsPage(login).open_alert_by_title(ALERT_B)
    detail = AlertDetailPage(login)
    assert detail.get_status() == "Resolved", "Alert B should be Resolved"
    assert detail.is_visible(detail.ESCALATE_BUTTON, timeout=10), (
        "Escalate button missing on Resolved alert"
    )


@pytest.mark.p1
@pytest.mark.alerts
def test_alert_b_action_menu_options(login):
    """TC-ALERT-DET-009 (Resolved) — + menu has only always-present items."""
    HomePage(login).go_to_alerts()
    AlertsPage(login).open_alert_by_title(ALERT_B)
    AlertDetailPage(login).open_action_menu()
    menu = AlertActionMenu(login)
    assert menu.is_visible_option("Add note"), "+ menu missing Add note"
    assert menu.is_visible_option("Mark as noise"), "+ menu missing Mark as noise"
    assert menu.is_visible_option("Create Incident"), "+ menu missing Create Incident"
    assert menu.is_visible_option("Share"), "+ menu missing Share"
    assert not menu.is_visible_option("Escalate"), "Escalate should be absent in Resolved menu"
    assert not menu.is_visible_option("Resolve"), "Resolve should be absent in Resolved menu"


@pytest.mark.p2
@pytest.mark.alerts
def test_escalate_primary_action_on_resolved(login):
    """TC-ALERT-ESC-002 — Escalate button (not in + menu) on Alert B (Resolved)."""
    HomePage(login).go_to_alerts()
    AlertsPage(login).open_alert_by_title(ALERT_B)
    detail = AlertDetailPage(login)
    assert detail.get_status() == "Resolved"
    detail.tap_escalate_button()
    to_sheet = AlertEscalateToSheet(login)
    to_sheet.confirm()
    esc = AlertEscalatePage(login)
    esc.close()


@pytest.mark.p2
@pytest.mark.alerts
def test_mark_as_noise_flow(login):
    """TC-ALERT-ACT-002 — Mark Alert B as Noise.

    No intermediate sheet — action applies immediately on tap.
    Post-action state confirmed from rootly-alert_detail_noise.xml:
    the Noise badge (name='Noise') appears alongside the status chip.
    """
    driver = login
    HomePage(driver).go_to_alerts()
    AlertsPage(driver).open_alert_by_title(ALERT_B)
    detail = AlertDetailPage(driver)
    detail.open_action_menu()
    AlertActionMenu(driver).tap_mark_as_noise()
    assert detail.has_noise_badge(), "Noise badge missing after Mark as noise"


# ====================================================================== #
# 5D — Triggered-state escalate: Alert A                                 #
# Alert A was never touched by the state machine — still Triggered.      #
# ====================================================================== #


@pytest.mark.p1
@pytest.mark.alerts
def test_escalate_from_action_menu_on_triggered(login):
    """TC-ALERT-ESC-001 — Escalate via + menu on Alert A (Triggered)."""
    driver = login
    HomePage(driver).go_to_alerts()
    AlertsPage(driver).open_alert_by_title(ALERT_A)
    detail = AlertDetailPage(driver)
    detail.open_action_menu()
    AlertActionMenu(driver).tap_escalate()

    to_sheet = AlertEscalateToSheet(driver)
    assert to_sheet.is_visible(), "'Escalate to' sheet did not appear"
    to_sheet.confirm()

    esc = AlertEscalatePage(driver)
    assert esc.is_visible(), "Escalate form did not open after confirming target"
    assert ALERT_A in esc.get_body_copy(), (
        "Escalate body copy should reference the alert title"
    )
    esc.open_responder_picker()
    picker = SelectResponders(driver)
    picker.wait_for_visible(picker.SEARCH_FIELD)  # sheet open + list ready
    picker.expand_category("People")
    picker.select("Kaushik Kolla")
    picker.done()
    esc.submit()
    esc.wait_for_toast("You have escalated successfully", timeout=15)


@pytest.mark.p2
@pytest.mark.alerts
def test_add_note_flow(login):
    """TC-ALERT-ACT-001 — empty submit rejected; typed note appears on Timeline."""
    driver = login
    HomePage(driver).go_to_alerts()
    AlertsPage(driver).open_alert_by_title(ALERT_A)
    detail = AlertDetailPage(driver)
    detail.open_action_menu()
    AlertActionMenu(driver).tap_add_note()

    sheet = AlertAddNoteSheet(driver)
    assert sheet.is_visible(), "Add note sheet did not open"

    # Empty submit — sheet must stay open
    sheet.submit()
    assert sheet.is_visible(timeout=2), (
        "Sheet closed on empty submit — empty note should be rejected"
    )

    # Submit a real note — no toast; sheet closing is the success signal
    note_text = "AutoTest note — add-note flow"
    sheet.fill_note(note_text)
    sheet.submit()
    assert not sheet.is_visible(timeout=5), "Sheet did not close after submitting note"

    detail.tap_timeline_tab()
    assert detail.timeline_has_event("note", timeout=10), (
        "Note event not visible on Timeline tab after adding"
    )


@pytest.mark.p1
@pytest.mark.alerts
@pytest.mark.e2e
def test_create_prefilled_incident_from_alert(login):
    """TC-ALERT-ACT-003 — + menu → Create Incident: alert title pre-filled;
    related incident appears in the Details tab after creation.

    Uses the same CreateIncidentPage form as standalone incident creation.
    """
    driver = login
    HomePage(driver).go_to_alerts()
    AlertsPage(driver).open_alert_by_title(ALERT_A)
    detail = AlertDetailPage(driver)
    detail.open_action_menu()
    AlertActionMenu(driver).tap_create_incident()

    form = CreateIncidentPage(driver)
    assert form.is_visible(), "Create Incident form did not open from action menu"

    # Known bug: app does not pre-fill the title when alert is in Triggered state.
    pre_filled = form.find(form.TITLE_FIELD, timeout=20).get_attribute("value") or ""
    assert ALERT_A in pre_filled, (
        f"Alert title not pre-filled in incident form (got {pre_filled!r})"
    )

    form.submit()
    form.wait_for_toast("Incident created successfully", timeout=15)

    # Navigate back to Alert A and verify the Related Incidents card is populated
    HomePage(driver).go_to_alerts()
    AlertsPage(driver).open_alert_by_title(ALERT_A)
    detail.tap_details_tab()
    assert detail.is_visible(detail.RELATED_INCIDENTS_CARD, timeout=10), (
        "Related Incidents card not visible on Details tab"
    )
    card_label = detail.find(detail.RELATED_INCIDENTS_CARD).get_attribute("label") or ""
    assert len(card_label) > len("Related Incidents"), (
        "Related Incidents card appears empty after creating incident from alert"
    )
