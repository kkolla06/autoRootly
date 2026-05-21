"""Settings drawer tests — the right-edge slide-out seen overlaying the Shifts screen.

Distinct from the full Settings page; covered separately so the two don't get
conflated. All tests skipped until raw_ios_xml/MISSING_XMLS.md (#21) lands.
"""
import pytest
from pages.home_page import HomePage
from pages.shifts_page import ShiftsPage
from pages.settings_drawer import SettingsDrawer


@pytest.mark.p2
@pytest.mark.settings
@pytest.mark.skip(reason="Settings drawer XML not captured — see raw_ios_xml/MISSING_XMLS.md (#21)")
def test_settings_drawer_distinct_from_full_page(login):
    """TC-SET-011 — Drawer overlay does not navigate away from Shifts permanently."""
    home = HomePage(login)
    home.go_to_shifts()
    shifts = ShiftsPage(login)

    # Reveal the drawer (exact gesture/trigger TBD from XML — likely an edge swipe
    # or a corner tap).
    # TODO: replace this placeholder with the captured trigger.

    drawer = SettingsDrawer(login)
    assert drawer.is_visible(), "Settings drawer not visible"
    drawer.dismiss()
    assert shifts.is_visible(), "Shifts screen should still be visible after dismissing drawer"
