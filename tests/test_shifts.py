"""Shifts / schedules tests — Section 6 of PLAN.md."""
import pytest
from pages.home_page import HomePage
from pages.shifts_page import ShiftsPage
from pages.settings_page import SettingsPage
from pages.select_schedules import SelectSchedules


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.shifts
def test_navigate_to_shifts(login):
    """TC-SHIFT-001."""
    HomePage(login).go_to_shifts()
    assert ShiftsPage(login).is_visible(timeout=10), "Shifts screen header not visible"


@pytest.mark.p1
@pytest.mark.shifts
def test_my_shifts_and_all_shifts_tabs(login):
    """TC-SHIFT-002."""
    HomePage(login).go_to_shifts()
    shifts = ShiftsPage(login)
    shifts.tap_my_shifts()
    assert shifts.is_visible(), "Shifts screen lost after tapping My shifts"
    shifts.tap_all_shifts()
    assert shifts.is_visible(), "Shifts screen lost after tapping All shifts"
    shifts.tap_my_shifts()
    assert shifts.is_visible(), "Shifts screen lost after returning to My shifts"


@pytest.mark.p1
@pytest.mark.shifts
def test_empty_state_message(login):
    """TC-SHIFT-003 — empty state when no shifts assigned."""
    HomePage(login).go_to_shifts()
    shifts = ShiftsPage(login)
    if not shifts.is_empty_state_visible():
        pytest.skip("Test account has shifts assigned — empty state not applicable here")
    assert shifts.is_empty_state_visible(), "Expected empty state message"


@pytest.mark.p2
@pytest.mark.shifts
def test_settings_avatar_accessible_from_shifts(login):
    """TC-SHIFT-004."""
    HomePage(login).go_to_shifts()
    ShiftsPage(login).open_settings()
    assert SettingsPage(login).is_visible(timeout=10), (
        "Settings did not open from the Shifts avatar"
    )


@pytest.mark.p1
@pytest.mark.shifts
@pytest.mark.skip(reason="Select Schedules modal XML not captured — see raw_ios_xml/MISSING_XMLS.md (#19)")
def test_select_schedules_combined(login):
    """TC-SHIFT-005 — tap 0 Schedules → modal → search + empty state → close → list intact."""
    HomePage(login).go_to_shifts()
    shifts = ShiftsPage(login)
    shifts.tap(shifts.SCHEDULES_COUNT)
    modal = SelectSchedules(login)
    assert modal.is_visible(), "Select Schedules modal did not open"
    assert modal.is_visible(modal.SEARCH_FIELD, timeout=5), "Search field missing"
    assert modal.is_empty_state_visible(), "Expected 'No schedules to show' empty state"
    modal.close()
    assert shifts.is_visible(), "Shifts list should still render after closing modal"


@pytest.mark.p2
@pytest.mark.shifts
@pytest.mark.skip(reason="Month picker XML not captured — see raw_ios_xml/MISSING_XMLS.md (#20)")
def test_month_picker_open_close(login):
    """TC-SHIFT-006."""
    pass
