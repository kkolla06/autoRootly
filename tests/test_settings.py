"""Settings tests — Section 7 of test plan."""
import os
import re
import pytest
from pages.home_page import HomePage
from pages.settings_page import SettingsPage


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.settings
def test_settings_opens_from_home(login):
    """TC-SET-001: Settings opens from the Home avatar."""
    HomePage(login).go_to_settings()
    assert SettingsPage(login).is_visible(timeout=10), "Settings did not load"


@pytest.mark.p1
@pytest.mark.settings
def test_settings_profile_info_combined(login):
    """TC-SET-002: Name, email, organization, and app version are all shown.

    Combined assertion — one round-trip checks every header-card element.
    """
    HomePage(login).go_to_settings()
    settings = SettingsPage(login)
    assert settings.has_profile_info(), (
        "Settings profile card missing one of: name / email / organization / about"
    )


@pytest.mark.p2
@pytest.mark.settings
def test_all_menu_items_tappable(login):
    """TC-SET-003: Remaining settings rows tap without crashing.

    Covers: Organization, Members, Language, Troubleshooting.
    Excluded — each has a dedicated test: Appearance, On-Call Notifications,
      Notification Settings, Clear Cache, About.
    Excluded — redirect out of app: Email Support, Update Contact Card.
    """
    HomePage(login).go_to_settings()
    settings = SettingsPage(login)
    for locator in settings.TAPPABLE_ROWS:
        settings.tap(locator)
        # Best-effort: tap back to return to Settings. If we never left Settings
        # (some rows expand inline), back is a no-op-ish gesture.
        try:
            settings.back()
        except Exception:
            pass
        # Re-anchor on Settings before moving to the next row.
        if not settings.is_visible(timeout=3):
            HomePage(login).go_to_settings()
        assert settings.is_visible(timeout=10), (
            f"Could not return to Settings after tapping {locator}"
        )


@pytest.mark.p1
@pytest.mark.settings
def test_on_call_notifications_opens(login):
    """TC-SET-004: On-Call Notifications sub-screen opens and returns to Settings."""
    HomePage(login).go_to_settings()
    settings = SettingsPage(login)
    settings.tap_on_call_notifications()
    assert settings.is_visible(settings.ON_CALL_NOTIFICATIONS_HEADER, timeout=10), (
        "On-Call Notifications sub-screen did not open"
    )
    settings.back()
    assert settings.is_visible(timeout=10), (
        "Did not return to Settings after closing On-Call Notifications"
    )


@pytest.mark.p1
@pytest.mark.settings
def test_notification_settings_opens(login):
    """TC-SET-005: Notification Settings opens iOS Settings for Rootly, then returns to app."""
    HomePage(login).go_to_settings()
    settings = SettingsPage(login)
    settings.tap_notification_settings()
    assert settings.is_ios_notification_settings_visible(), (
        "iOS Settings Rootly notification screen did not open"
    )
    login.activate_app(os.getenv("APP_BUNDLE_ID"))
    assert settings.is_visible(timeout=10), (
        "Settings screen did not restore after returning from iOS Settings"
    )


@pytest.mark.p2
@pytest.mark.settings
def test_appearance_row_opens(login):
    """TC-SET-006: Appearance sub-screen opens and all three theme options are selectable."""
    HomePage(login).go_to_settings()
    settings = SettingsPage(login)
    settings.tap_appearance()
    assert settings.is_appearance_visible(), "Appearance sub-screen did not open"

    settings.tap_appearance_light()
    assert settings.is_appearance_visible(), "Left Appearance screen after tapping Light"

    settings.tap_appearance_dark()
    assert settings.is_appearance_visible(), "Left Appearance screen after tapping Dark"

    settings.tap_appearance_system()
    assert settings.is_appearance_visible(), "Left Appearance screen after tapping System"

    settings.back()
    assert settings.is_visible(timeout=10), "Did not return to Settings after closing Appearance"


@pytest.mark.p1
@pytest.mark.settings
def test_clear_cache_shows_confirmation(login):
    """TC-SET-007: Clear Cache & Data presents a confirmation (it does NOT clear instantly)."""
    HomePage(login).go_to_settings()
    settings = SettingsPage(login)
    settings.tap_clear_cache_and_data()
    assert settings.is_visible(settings.CONFIRM_CLEAR_BUTTON, timeout=10), (
        "Clear Cache & Data must show a confirmation before clearing"
    )
    # Dismiss to avoid actually logging out for this isolated test.
    settings.cancel_clear_cache()


@pytest.mark.p1
@pytest.mark.settings
def test_app_version_format(login):
    """TC-SET-008: About sub-screen — device name, version format, and all three web redirects."""
    HomePage(login).go_to_settings()
    settings = SettingsPage(login)
    settings.tap_about()
    assert settings.is_about_visible(), "About sub-screen did not open"

    assert settings.is_visible(settings.ABOUT_DEVICE_NAME, timeout=5), (
        "Device name field not visible on About screen"
    )
    device_name = settings.find(settings.ABOUT_DEVICE_NAME).get_attribute("value")
    assert device_name, "Device name field is empty"

    assert settings.is_visible(settings.ABOUT_SYSTEM_STATUS, timeout=5), (
        "Rootly System Status link not visible"
    )
    assert settings.is_visible(settings.ABOUT_PRIVACY_POLICY, timeout=5), (
        "Privacy Policy link not visible"
    )
    assert settings.is_visible(settings.ABOUT_TERMS_OF_USE, timeout=5), (
        "Terms of Use link not visible"
    )

    version = settings.get_app_version()
    assert re.match(r"^\d+\.\d+\.\d+$", version), (
        f"Unexpected app version format: '{version}'"
    )

    settings.tap(settings.ABOUT_SYSTEM_STATUS)
    assert settings.is_safari_at("status.rootly.com"), (
        "System Status did not open status.rootly.com in Safari"
    )
    login.activate_app(os.getenv("APP_BUNDLE_ID"))
    assert settings.is_about_visible(timeout=10), (
        "About screen did not restore after returning from System Status"
    )

    settings.tap(settings.ABOUT_PRIVACY_POLICY)
    assert settings.is_visible(settings.SAFARI_PRIVACY_POLICY_TITLE, timeout=10), (
        "Privacy Policy did not open correctly in Safari"
    )
    login.activate_app(os.getenv("APP_BUNDLE_ID"))
    assert settings.is_about_visible(timeout=10), (
        "About screen did not restore after returning from Privacy Policy"
    )

    settings.tap(settings.ABOUT_TERMS_OF_USE)
    assert settings.is_visible(settings.SAFARI_TERMS_OF_USE_TITLE, timeout=10), (
        "Terms of Use did not open correctly in Safari"
    )
    login.activate_app(os.getenv("APP_BUNDLE_ID"))
    assert settings.is_about_visible(timeout=10), (
        "About screen did not restore after returning from Terms of Use"
    )

    settings.back()
    assert settings.is_visible(timeout=10), "Did not return to Settings after closing About"


@pytest.mark.p1
@pytest.mark.settings
def test_back_navigation_from_settings(login):
    """TC-SET-010: Tapping back returns the user to the Home screen."""
    home = HomePage(login)
    home.go_to_settings()
    settings = SettingsPage(login)
    settings.back()
    assert home.is_home_visible(timeout=10), (
        "Back from Settings should return to Home"
    )
