"""Home dashboard tests — Section 3 of PLAN.md."""
import pytest
from pages.home_page import HomePage
from pages.settings_page import SettingsPage
from pages.alerts.alerts_page import AlertsPage
from pages.alerts.alert_detail_page import AlertDetailPage


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.home
def test_home_loads_with_all_sections(login):
    """TC-HOME-001."""
    home = HomePage(login)
    assert home.is_home_visible(), "Home indicator missing"
    assert home.has_all_widgets(), (
        "One or more dashboard widgets are missing "
        "(coverage_requests / ongoing_alerts / ongoing_incidents / Time to ack / Time to resolve)"
    )
    assert home.has_bottom_nav(), "Bottom nav bar is incomplete on Home"
    assert home.is_visible(home.ONCALL_STATUS, timeout=5), "On-call status header missing"


@pytest.mark.p1
@pytest.mark.home
def test_oncall_status_text_is_valid(login):
    """TC-HOME-002."""
    status = HomePage(login).get_oncall_status()
    assert status in ("You're on-call", "You're not on-call"), (
        f"Unexpected on-call status text: '{status}'"
    )


@pytest.mark.p1
@pytest.mark.home
def test_settings_avatar_opens_settings(login):
    """TC-HOME-003."""
    HomePage(login).go_to_settings()
    assert SettingsPage(login).is_visible(timeout=5), "Settings did not load from Home avatar"


@pytest.mark.p2
@pytest.mark.home
def test_home_is_scrollable(login):
    """TC-HOME-004."""
    home = HomePage(login)
    home.scroll_down()
    assert home.is_home_visible(), "Home should still be visible after a scroll"


# --------------------------------------------------------------------------- #
# Paged-home state — depends on paged_alert fixture (XMLs #1, #5, #12)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.home
def test_paged_home_banner_after_self_page(paged_alert, login):
    """TC-HOME-005 — self-page → Home shows red banner + View Alert + Ongoing Alerts incremented."""
    home = HomePage(login)
    home.go_home()
    assert home.is_paged(timeout=5), "Paged-home banner did not appear after self-page"
    assert home.is_visible(home.VIEW_ALERT_BUTTON, timeout=5), "View Alert button missing"
    count = home.get_ongoing_alerts_count()
    assert count is None or count >= 1, (
        f"Expected at least 1 ongoing alert after self-page, got {count}"
    )


@pytest.mark.p1
@pytest.mark.home
def test_view_alert_opens_paged_alert(paged_alert, login):
    """TC-HOME-006 — Tap View Alert → detail screen for the self-paged alert."""
    home = HomePage(login)
    home.go_home()
    assert home.is_paged(timeout=5), "Paged-home banner not present"
    banner_id = home.get_paged_alert_id() if paged_alert.get("id") is None else paged_alert["id"]
    home.tap_view_alert()
    detail = AlertDetailPage(login)
    detail.wait_for_visible(detail.DETAILS_TAB, timeout=5)
    assert detail.get_alert_id() == banner_id, (
        f"Opened alert id {detail.get_alert_id()} != banner id {banner_id}"
    )


@pytest.mark.p1
@pytest.mark.home
def test_paged_home_clears_after_resolve(paged_alert, login):
    """TC-HOME-007 — After resolving the paged alert, Home returns to normal state."""
    home = HomePage(login)
    home.go_to_alerts()
    AlertsPage(login).open_first_alert()
    detail = AlertDetailPage(login)
    detail.slide_to_ack()
    detail.wait_for_visible(detail.SLIDE_TO_RESOLVE, timeout=5)
    detail.slide_to_resolve()
    detail.wait_for_visible(detail.ESCALATE_BUTTON, timeout=5)

    home.go_home()
    assert not home.is_paged(timeout=5), "Paged banner should be gone after resolving the alert"
