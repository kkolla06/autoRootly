"""Cross-screen navigation tests — Section 8 of PLAN.md."""
import pytest
from pages.home_page import HomePage
from pages.alerts.alerts_page import AlertsPage
from pages.alerts.alert_detail_page import AlertDetailPage
from pages.incidents.incident_list_page import IncidentListPage
from pages.incidents.incident_detail_page import IncidentDetailPage
from pages.shifts_page import ShiftsPage
from pages.settings_page import SettingsPage
from pages.create_menu import CreateMenu


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.navigation
def test_bottom_nav_present_across_main_screens(login):
    """TC-NAV-001 — cycle Home → Alerts → Incidents → Shifts → Home."""
    home = HomePage(login)
    assert home.has_bottom_nav(), "Bottom nav missing on Home"

    home.go_to_alerts()
    assert AlertsPage(login).is_alerts_list_visible(), "Alerts did not load via nav tab"
    assert home.has_bottom_nav(), "Bottom nav missing on Alerts"

    home.go_to_incidents()
    assert IncidentListPage(login).is_list_visible(), "Incidents did not load via nav tab"
    assert home.has_bottom_nav(), "Bottom nav missing on Incidents"

    home.go_to_shifts()
    assert ShiftsPage(login).is_visible(timeout=10), "Shifts did not load via nav tab"
    assert home.has_bottom_nav(), "Bottom nav missing on Shifts"

    home.go_home()
    assert home.is_home_visible(timeout=10), "Home did not load via Home tab"


@pytest.mark.p1
@pytest.mark.navigation
def test_menu_toggle_opens_secondary_options(login):
    """TC-NAV-003."""
    home = HomePage(login)
    home.open_menu()
    assert home.driver.session_id is not None, "App appears to have terminated"


@pytest.mark.p1
@pytest.mark.navigation
def test_deep_navigation_back_works(login):
    """TC-NAV-004."""
    home = HomePage(login)

    home.go_to_incidents()
    IncidentListPage(login).open_first_incident()
    detail_inc = IncidentDetailPage(login)
    assert detail_inc.is_detail_visible(), "Detail not visible"
    detail_inc.tap_back()
    assert IncidentListPage(login).is_list_visible(), "Back did not return to incident list"

    home.go_to_alerts()
    alerts = AlertsPage(login)
    alerts.open_first_alert()
    detail = AlertDetailPage(login)
    detail.tap_timeline_tab()
    detail.tap_back()
    assert alerts.is_alerts_list_visible(), "Back did not return to alerts list"


@pytest.mark.p2
@pytest.mark.navigation
def test_settings_avatar_consistent_across_screens(login):
    """TC-NAV-005."""
    home = HomePage(login)

    steps = [
        (home.go_to_incidents, lambda: IncidentListPage(login).open_settings()),
        (home.go_to_alerts,    lambda: AlertsPage(login).open_settings()),
        (home.go_to_shifts,    lambda: ShiftsPage(login).open_settings()),
    ]
    for go, open_settings in steps:
        go()
        open_settings()
        assert SettingsPage(login).is_visible(timeout=10), (
            f"Settings did not open via avatar after navigating to {go.__name__}"
        )
        SettingsPage(login).back()


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.navigation
def test_plus_tab_opens_create_menu(login):
    """TC-NAV-006 — tap '+' → Create menu shows the 3 entries → X closes."""
    home = HomePage(login)
    home.open_menu()
    menu = CreateMenu(login)
    assert menu.is_visible(), "Create menu sheet did not open"
    assert menu.is_visible(menu.CREATE_INCIDENT, timeout=3), "Create Incident row missing"
    assert menu.is_visible(menu.CREATE_ALERT, timeout=3), "Create Alert row missing"
    assert menu.is_visible(menu.CREATE_OVERRIDE, timeout=3), "Create Override row missing"

    menu.close()
    assert home.has_bottom_nav(), "Bottom nav should be restored after closing the sheet"
