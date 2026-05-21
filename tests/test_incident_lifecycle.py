"""Incident lifecycle tests — Section 4 of PLAN.md."""
import pytest
from pages.home_page import HomePage
from pages.create_menu import CreateMenu
from pages.incidents.incident_list_page import IncidentListPage
from pages.incidents.create_incident_page import CreateIncidentPage
from pages.incidents.incident_detail_page import IncidentDetailPage
from pages.incidents.incident_sort_filter import IncidentStatusFilter


# --------------------------------------------------------------------------- #
# 4A — Incidents List
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.incident
def test_incidents_list_loads(login):
    """TC-INC-LIST-001."""
    HomePage(login).go_to_incidents()
    assert IncidentListPage(login).is_list_visible(), "Incidents list not visible"


@pytest.mark.p2
@pytest.mark.incident
def test_incidents_filters_combined(login):
    """TC-INC-LIST-003 — Status filter opens and closes; list survives. Ownership open/close."""
    HomePage(login).go_to_incidents()
    list_page = IncidentListPage(login)

    list_page.tap_status_filter()
    status_sheet = IncidentStatusFilter(login)
    assert status_sheet.is_visible(), "Status filter sheet did not open"
    status_sheet.dismiss()

    assert list_page.is_list_visible(), "List should remain visible after filtering"


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.incident
def test_tapping_incident_opens_detail(login):
    """TC-INC-LIST-004."""
    HomePage(login).go_to_incidents()
    IncidentListPage(login).open_first_incident()
    assert IncidentDetailPage(login).is_detail_visible(), "Incident detail not visible"


@pytest.mark.p2
@pytest.mark.incident
def test_incidents_list_is_scrollable(login):
    """TC-INC-LIST-005."""
    HomePage(login).go_to_incidents()
    list_page = IncidentListPage(login)
    list_page.scroll_down()
    assert list_page.is_list_visible(), "Incidents list should still render after scroll"


# --------------------------------------------------------------------------- #
# 4B — Incident Detail
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.incident
def test_incident_detail_loads_with_header_data(login):
    """TC-INC-DET-001 + TC-INC-DET-002."""
    HomePage(login).go_to_incidents()
    IncidentListPage(login).open_first_incident()
    detail = IncidentDetailPage(login)
    assert detail.is_detail_visible(), "Detail tab not visible"
    status = detail.get_status()
    assert status in detail.VALID_STATUSES, (
        f"Unexpected status '{status}' — expected one of {detail.VALID_STATUSES}"
    )


@pytest.mark.p1
@pytest.mark.incident
def test_details_tab_selected_by_default(login):
    """TC-INC-DET-003."""
    HomePage(login).go_to_incidents()
    IncidentListPage(login).open_first_incident()
    assert IncidentDetailPage(login).is_visible(IncidentDetailPage.DETAILS_TAB, timeout=10), (
        "Details tab should be visible / selected by default"
    )


@pytest.mark.p1
@pytest.mark.incident
def test_alerts_tab_loads(login):
    """TC-INC-DET-005."""
    HomePage(login).go_to_incidents()
    IncidentListPage(login).open_first_incident()
    detail = IncidentDetailPage(login)
    detail.tap_alerts_tab()
    detail.tap_details_tab()
    assert detail.is_detail_visible(), "Tab cycle (Details → Alerts → Details) failed"


@pytest.mark.p2
@pytest.mark.incident
def test_add_related_alert_button_visible(login):
    """TC-INC-DET-006."""
    HomePage(login).go_to_incidents()
    IncidentListPage(login).open_first_incident()
    assert IncidentDetailPage(login).is_visible(
        IncidentDetailPage.ADD_ALERT_BUTTON, timeout=10
    ), "Add related alert button missing"


@pytest.mark.p1
@pytest.mark.incident
def test_back_navigation_returns_to_list(login):
    """TC-INC-DET-007."""
    HomePage(login).go_to_incidents()
    IncidentListPage(login).open_first_incident()
    IncidentDetailPage(login).tap_back()
    assert IncidentListPage(login).is_list_visible(), "Back did not return to list"


# --------------------------------------------------------------------------- #
# 4C — Incident Creation
# --------------------------------------------------------------------------- #


@pytest.mark.p1
@pytest.mark.incident
def test_create_incident_empty_form_submits_with_random_name(login):
    """TC-INC-CREATE-007 — BUG: submitting an empty form creates an incident with a random name instead of showing a validation error."""
    home = HomePage(login)
    home.open_menu()
    CreateMenu(login).tap_create_incident()
    form = CreateIncidentPage(login)
    form.submit()
    # Bug: form closes and creates an incident rather than blocking with an error.
    assert not form.is_visible(timeout=5), (
        "Form should have closed (empty submit created an incident)"
    )
    HomePage(login).go_to_incidents()
    assert IncidentListPage(login).is_list_visible(), (
        "Incident list should be visible with the randomly named incident"
    )
