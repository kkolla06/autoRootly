"""Landing screen tests — Section 1 of test plan."""
import os
import pytest
from pages.landing_page import LandingPage
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.settings_page import SettingsPage


def _ensure_landing(driver):
    """If a session is active, log out via Clear Cache & Data (the working logout path)
    so the Landing screen is visible. See test plan §2G and known web cache bug."""
    landing = LandingPage(driver)
    if landing.is_visible(timeout=3):
        return

    home = HomePage(driver)
    if home.is_home_visible(timeout=10):
        home.go_to_settings()
        settings = SettingsPage(driver)
        settings.tap_clear_cache_and_data()
        # Confirm dialog — best-effort: only tap if it appears
        if settings.is_visible(settings.CONFIRM_CLEAR_BUTTON, timeout=3):
            settings.confirm_clear_cache()
        landing.wait_for_visible(landing.LOG_IN_BUTTON, timeout=20)


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.landing
def test_landing_screen_loads_on_cold_launch(driver):
    """TC-LAND-001: Landing screen shows on cold launch with Log in button + tagline."""
    _ensure_landing(driver)
    landing = LandingPage(driver)
    assert landing.is_visible(), "Landing screen not visible on cold launch"
    assert landing.is_visible(landing.TAGLINE, timeout=5), (
        "Landing tagline not visible — Landing may not have fully rendered"
    )


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.landing
def test_log_in_button_opens_web_login_form(driver):
    """TC-LAND-002: Tapping Log in opens the embedded web login form."""
    _ensure_landing(driver)
    LandingPage(driver).tap_log_in()
    login = LoginPage(driver)
    assert login.is_form_visible(timeout=15), (
        "Web login form did not appear after tapping Log in"
    )

# TODO: Skipped till login is fixed
# @pytest.mark.p1
# @pytest.mark.landing
# @pytest.mark.login
# def test_landing_shown_after_clear_cache_logout(driver):
#     """TC-LAND-003: Successful logout via Clear Cache & Data returns the user to Landing."""
#     home = HomePage(driver)

#     # If we're not already logged in, do a login first so we have a session to log out of.
#     if not home.is_home_visible(timeout=3):
#         LoginPage(driver).login(
#             email=os.getenv("ROOTLY_TEST_EMAIL"),
#             password=os.getenv("ROOTLY_TEST_PASSWORD"),
#         )
#         home.wait_for_visible(home.HOME_INDICATOR, timeout=30)

#     home.go_to_settings()
#     settings = SettingsPage(driver)
#     settings.tap_clear_cache_and_data()
#     if settings.is_visible(settings.CONFIRM_CLEAR_BUTTON, timeout=5):
#         settings.confirm_clear_cache()

#     assert LandingPage(driver).is_visible(timeout=20), (
#         "Expected Landing screen after Clear Cache & Data logout"
#     )
