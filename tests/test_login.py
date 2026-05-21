"""Authentication tests — Section 2 of test plan.

Covers: Web login form discovery (2A), email/password (2B), SSO (2C),
Google SSO (2D), Slack SSO (2E), Create Account (2F), Logout (2G), edges.
"""
import os
import pytest
from pages.landing_page import LandingPage
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.settings_page import SettingsPage


def _email():
    return os.getenv("ROOTLY_TEST_EMAIL")


def _password():
    return os.getenv("ROOTLY_TEST_PASSWORD")


def _ensure_landing(driver):
    """Make sure we're on the Landing screen (log out via Clear Cache & Data if needed)."""
    landing = LandingPage(driver)
    if landing.is_visible(timeout=3):
        return
    home = HomePage(driver)
    if home.is_home_visible(timeout=3):
        home.go_to_settings()
        settings = SettingsPage(driver)
        settings.tap_clear_cache_and_data()
        if settings.is_visible(settings.CONFIRM_CLEAR_BUTTON, timeout=5):
            settings.confirm_clear_cache()
        landing.wait_for_visible(landing.LOG_IN_BUTTON, timeout=20)


def _open_login_form(driver):
    _ensure_landing(driver)
    LandingPage(driver).tap_log_in()
    LoginPage(driver).wait_for_visible(LoginPage.EMAIL_FIELD, timeout=15)


# --------------------------------------------------------------------------- #
# 2A — Web Login Form Discovery
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.login
def test_web_login_form_shows_all_expected_fields(driver):
    """TC-AUTH-001: All key elements of the web login form are present.

    Single check that guards every downstream login path — if any of these are
    missing, several other tests will fail for the same root cause.
    """
    _open_login_form(driver)
    login = LoginPage(driver)
    for label, locator in [
        ("email", login.EMAIL_FIELD),
        ("password", login.PASSWORD_FIELD),
        ("Sign in", login.SIGN_IN_BUTTON),
        ("Remember me", login.REMEMBER_ME_SWITCH),
        ("SSO link", login.SSO_LINK),
        ("Google login", login.GOOGLE_LOGIN_LINK),
        ("Slack login", login.SLACK_LOGIN_LINK),
        ("Cancel", login.CANCEL_BUTTON),
    ]:
        assert login.is_visible(locator, timeout=5), f"Login form: {label} not visible"


@pytest.mark.p1
@pytest.mark.login
def test_cancel_from_web_login_returns_to_landing(driver):
    """TC-AUTH-002: Cancel button returns the user to Landing."""
    _open_login_form(driver)
    LoginPage(driver).cancel()
    assert LandingPage(driver).is_visible(timeout=10), (
        "Did not return to Landing after Cancel"
    )


# --------------------------------------------------------------------------- #
# 2B — Email / Password Login
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.login
def test_valid_credentials_reach_home(driver):
    """TC-AUTH-003: Correct email + password lands the user on the Home screen."""
    home = HomePage(driver)
    if not home.is_home_visible(timeout=3):
        LoginPage(driver).login(email=_email(), password=_password())
    assert home.is_home_visible(timeout=30), "Home not visible after valid login"


@pytest.mark.p1
@pytest.mark.login
def test_combined_negative_login_with_cancel_refresh(driver):
    """TC-AUTH-004: Chain all negative login scenarios, using Cancel-refresh between
    each, then complete the happy path. Each Cancel acts as a clean form reset
    (per user-suggested combination pattern)."""
    _ensure_landing(driver)
    login = LoginPage(driver)

    # 1. Empty email
    login.open_from_landing()
    login.type_text(login.PASSWORD_FIELD, "doesntmatter")
    login.tap(login.SIGN_IN_BUTTON)
    # Either inline error appears, or we stay on the form. Both are acceptable
    # negative-paths — assert we did NOT proceed to Home.
    assert not HomePage(driver).is_home_visible(timeout=3), (
        "Empty email accepted — login should not have proceeded"
    )
    login.cancel()

    # 2. Empty password
    login.open_from_landing()
    login.type_text(login.EMAIL_FIELD, _email())
    login.tap(login.SIGN_IN_BUTTON)
    assert not HomePage(driver).is_home_visible(timeout=3), (
        "Empty password accepted — login should not have proceeded"
    )
    login.cancel()

    # 3. Invalid email format
    login.open_from_landing()
    login.type_text(login.EMAIL_FIELD, "notanemail")
    login.type_text(login.PASSWORD_FIELD, "doesntmatter")
    login.tap(login.SIGN_IN_BUTTON)
    assert not HomePage(driver).is_home_visible(timeout=3), (
        "Invalid email format accepted — login should not have proceeded"
    )
    login.cancel()

    # 4. Happy path
    login.open_from_landing()
    login.type_text(login.EMAIL_FIELD, _email())
    login.type_text(login.PASSWORD_FIELD, _password())
    login.tap(login.SIGN_IN_BUTTON)
    assert HomePage(driver).is_home_visible(timeout=30), (
        "Final happy-path login did not reach Home"
    )


@pytest.mark.p1
@pytest.mark.login
def test_wrong_password_shows_error_or_stays_on_form(driver):
    """TC-AUTH-005: Wrong password keeps the user on the login form (and ideally
    surfaces an error). We accept either form-still-visible OR explicit error
    text — the WebView's error rendering isn't fully captured in XML."""
    _ensure_landing(driver)
    login = LoginPage(driver)
    login.open_from_landing()
    login.type_text(login.EMAIL_FIELD, _email())
    login.type_text(login.PASSWORD_FIELD, "definitely-wrong-password")
    login.tap(login.SIGN_IN_BUTTON)

    home = HomePage(driver)
    assert not home.is_home_visible(timeout=5), (
        "Wrong password should not reach Home"
    )
    assert login.is_form_visible(timeout=5), (
        "User should remain on the login form after wrong password"
    )


@pytest.mark.p2
@pytest.mark.login
def test_show_hide_password_toggle(driver):
    """TC-AUTH-006: Toggle reveals the password (the field type flips from
    SecureTextField to TextField)."""
    _open_login_form(driver)
    login = LoginPage(driver)
    login.type_text(login.PASSWORD_FIELD, "secret123")
    assert login.password_is_masked(), "Password should start masked"
    login.toggle_show_password()
    # After toggling, a plain TextField with the value should appear.
    assert not login.password_is_masked(), (
        "Password should be unmasked after toggling the show-password button"
    )


@pytest.mark.p2
@pytest.mark.login
def test_remember_me_toggle_works(driver):
    """TC-AUTH-007: Remember me toggle state changes when tapped."""
    _open_login_form(driver)
    login = LoginPage(driver)
    initial = login.remember_me_state()
    login.toggle_remember_me()
    after = login.remember_me_state()
    assert initial != after, (
        f"Remember me did not toggle (state stayed at '{initial}')"
    )


# --------------------------------------------------------------------------- #
# 2C — SSO (Generic)
# --------------------------------------------------------------------------- #


@pytest.mark.p1
@pytest.mark.login
@pytest.mark.skip(reason="SSO entry-screen XML not captured — see raw_ios_xml/MISSING_XMLS.md (#7)")
def test_sso_link_opens_sso_configuration(driver):
    """TC-AUTH-008: Tapping the SSO link opens the SSO subdomain entry screen."""
    _open_login_form(driver)
    LoginPage(driver).tap_sso()
    # TODO: assert SSO subdomain screen — locator pending


@pytest.mark.p1
@pytest.mark.login
@pytest.mark.skip(reason="SSO flow XML not captured — see raw_ios_xml/MISSING_XMLS.md (#7)")
def test_sso_valid_login_reaches_home(driver):
    """TC-AUTH-009: SSO login completes and reaches Home."""
    pass


# --------------------------------------------------------------------------- #
# 2D — Google SSO
# --------------------------------------------------------------------------- #


@pytest.mark.p1
@pytest.mark.login
@pytest.mark.skip(reason="Google OAuth XML not captured — see raw_ios_xml/MISSING_XMLS.md (#8)")
def test_google_sso_opens_google_auth(driver):
    """TC-AUTH-010: Google login icon opens Google's OAuth sheet."""
    _open_login_form(driver)
    LoginPage(driver).tap_google()
    # TODO: assert Google OAuth sheet present


@pytest.mark.p1
@pytest.mark.login
@pytest.mark.skip(reason="Google OAuth XML not captured — see raw_ios_xml/MISSING_XMLS.md (#8)")
def test_google_sso_valid_reaches_home(driver):
    """TC-AUTH-011: Completing Google sign-in reaches Home."""
    pass


@pytest.mark.p2
@pytest.mark.login
@pytest.mark.skip(reason="Google OAuth XML not captured — see raw_ios_xml/MISSING_XMLS.md (#8)")
def test_google_sso_cancel_returns_to_login_form(driver):
    """TC-AUTH-012: Cancelling Google auth returns to the web login form."""
    pass


# --------------------------------------------------------------------------- #
# 2E — Slack SSO
# --------------------------------------------------------------------------- #


@pytest.mark.p1
@pytest.mark.login
@pytest.mark.skip(reason="Slack OAuth XML not captured — see raw_ios_xml/MISSING_XMLS.md (#9)")
def test_slack_sso_opens_slack_auth(driver):
    """TC-AUTH-013: Slack login icon opens Slack's OAuth sheet."""
    _open_login_form(driver)
    LoginPage(driver).tap_slack()
    # TODO: assert Slack OAuth sheet present


@pytest.mark.p1
@pytest.mark.login
@pytest.mark.skip(reason="Slack OAuth XML not captured — see raw_ios_xml/MISSING_XMLS.md (#9)")
def test_slack_sso_valid_reaches_home(driver):
    """TC-AUTH-014: Completing Slack sign-in reaches Home."""
    pass


@pytest.mark.p2
@pytest.mark.login
@pytest.mark.skip(reason="Slack OAuth XML not captured — see raw_ios_xml/MISSING_XMLS.md (#9)")
def test_slack_sso_cancel_returns_to_login_form(driver):
    """TC-AUTH-015: Cancelling Slack auth returns to the web login form."""
    pass


# --------------------------------------------------------------------------- #
# 2F — Create Account
# --------------------------------------------------------------------------- #


@pytest.mark.p2
@pytest.mark.login
@pytest.mark.skip(reason="Create Account entry XML not captured — see raw_ios_xml/MISSING_XMLS.md (#1)")
def test_create_account_entry_point_discoverable(driver):
    """TC-AUTH-016: A Create Account / Sign Up link is reachable from the web form."""
    pass


@pytest.mark.p2
@pytest.mark.login
@pytest.mark.skip(reason="Create Account flow XML not captured — see raw_ios_xml/MISSING_XMLS.md (#1)")
def test_create_account_valid_info(driver):
    """TC-AUTH-017: Submitting valid info creates an account."""
    pass


@pytest.mark.p2
@pytest.mark.login
@pytest.mark.skip(reason="Create Account flow XML not captured — see raw_ios_xml/MISSING_XMLS.md (#1)")
def test_create_account_duplicate_email(driver):
    """TC-AUTH-018: Submitting an already-registered email surfaces an error."""
    pass


@pytest.mark.p3
@pytest.mark.login
@pytest.mark.skip(reason="Create Account flow XML not captured — see raw_ios_xml/MISSING_XMLS.md (#1)")
def test_create_account_weak_password(driver):
    """TC-AUTH-019: Weak passwords are rejected."""
    pass


@pytest.mark.p3
@pytest.mark.login
@pytest.mark.skip(reason="Create Account flow XML not captured — see raw_ios_xml/MISSING_XMLS.md (#1)")
def test_create_account_cancel(driver):
    """TC-AUTH-020: Cancelling create-account returns to the login form."""
    pass


# --------------------------------------------------------------------------- #
# 2G — Logout
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.login
def test_primary_logout_via_clear_cache_and_data(login):
    """TC-AUTH-021: The *working* logout path is Settings → Clear Cache & Data → confirm.

    Per the documented web cache bug, only Clear Cache & Data fully clears state.
    """
    driver = login
    HomePage(driver).go_to_settings()
    settings = SettingsPage(driver)
    settings.tap_clear_cache_and_data()
    assert settings.is_visible(settings.CONFIRM_CLEAR_BUTTON, timeout=10), (
        "Clear Cache & Data should show a confirmation dialog"
    )
    settings.confirm_clear_cache()
    assert LandingPage(driver).is_visible(timeout=20), (
        "Expected Landing after Clear Cache & Data confirm"
    )


@pytest.mark.p1
@pytest.mark.login
def test_clear_cache_confirmation_can_be_cancelled(login):
    """TC-AUTH-022: Dismissing the Clear Cache confirmation keeps the user logged in."""
    driver = login
    HomePage(driver).go_to_settings()
    settings = SettingsPage(driver)
    settings.tap_clear_cache_and_data()
    assert settings.is_visible(settings.CANCEL_CLEAR_BUTTON, timeout=10), (
        "Cancel button should exist on the confirmation dialog"
    )
    settings.cancel_clear_cache()
    assert settings.is_visible(timeout=5), (
        "User should remain on Settings after cancelling Clear Cache"
    )


@pytest.mark.p2
@pytest.mark.login
def test_log_out_button_known_web_cache_bug(login):
    """TC-AUTH-023: The Log Out button transitions to Landing — but is known to leave
    web cache that prevents re-login in the embedded WebView. This test verifies
    only the logout transition; re-login is intentionally NOT exercised here
    (covered by TC-AUTH-021 / TC-AUTH-024 via Clear Cache & Data instead).
    """
    driver = login
    HomePage(driver).go_to_settings()
    settings = SettingsPage(driver)
    # The Log Out row is not visible in some captured XMLs (off-screen); scroll to it.
    if not settings.is_visible(settings.LOG_OUT, timeout=3):
        settings.scroll_down()
    settings.tap_log_out()
    assert LandingPage(driver).is_visible(timeout=20), (
        "Log Out should transition to Landing (regardless of re-login bug)"
    )


@pytest.mark.p1
@pytest.mark.login
def test_re_login_after_clear_cache_works(driver):
    """TC-AUTH-024: After Clear Cache & Data, a fresh login succeeds.

    Confirms the primary logout path fully clears state (in contrast to the
    Log Out button per TC-AUTH-023).
    """
    home = HomePage(driver)
    if home.is_home_visible(timeout=3):
        home.go_to_settings()
        settings = SettingsPage(driver)
        settings.tap_clear_cache_and_data()
        if settings.is_visible(settings.CONFIRM_CLEAR_BUTTON, timeout=5):
            settings.confirm_clear_cache()
        LandingPage(driver).wait_for_visible(
            LandingPage.LOG_IN_BUTTON, timeout=20
        )

    LoginPage(driver).login(email=_email(), password=_password())
    assert home.is_home_visible(timeout=30), (
        "Re-login after Clear Cache & Data did not reach Home"
    )


# --------------------------------------------------------------------------- #
# Edge cases (auth)
# --------------------------------------------------------------------------- #


@pytest.mark.p3
@pytest.mark.login
@pytest.mark.edge
def test_email_with_leading_trailing_spaces(driver):
    """TC-AUTH-E01: Email with surrounding whitespace is trimmed and accepted (or
    rejected with a clear error)."""
    _ensure_landing(driver)
    login = LoginPage(driver)
    login.open_from_landing()
    login.type_text(login.EMAIL_FIELD, f"  {_email()}  ")
    login.type_text(login.PASSWORD_FIELD, _password())
    login.tap(login.SIGN_IN_BUTTON)
    # Either we make it to Home (server trims) or stay on form (server rejects).
    # A crash or stuck spinner is NOT acceptable.
    home_visible = HomePage(driver).is_home_visible(timeout=15)
    form_visible = login.is_form_visible(timeout=3)
    assert home_visible or form_visible, (
        "App ended up in an unknown state with whitespace-padded email"
    )


@pytest.mark.p2
@pytest.mark.login
@pytest.mark.edge
@pytest.mark.skip(reason="iOS Passwords autofill modal XML not captured — see raw_ios_xml/MISSING_XMLS.md (#24)")
def test_autofill_modal_dismiss_keeps_form_usable(driver):
    """TC-AUTH-E03 — iOS Face ID/Passwords autofill modal can be dismissed and
    manual entry still works.

    The walkthrough recording shows this modal appearing automatically once
    the embedded login form loads, partially covering the email/password
    fields. We need to confirm the dismiss gesture (keyboard icon tap) leaves
    the form interactive.
    """
    pass


@pytest.mark.p3
@pytest.mark.login
@pytest.mark.edge
@pytest.mark.skip(reason="iOS Passwords autofill modal XML not captured — see raw_ios_xml/MISSING_XMLS.md (#24)")
def test_autofill_modal_cancel_then_manual_entry(driver):
    """TC-AUTH-E04 — Cancel from the autofill modal → email field still tappable + typeable."""
    pass


@pytest.mark.p2
@pytest.mark.login
@pytest.mark.edge
def test_double_tap_sign_in(driver):
    """TC-AUTH-E02: Double-tapping Sign in should not produce duplicate sessions
    or unexpected errors."""
    _ensure_landing(driver)
    login = LoginPage(driver)
    login.open_from_landing()
    login.type_text(login.EMAIL_FIELD, _email())
    login.type_text(login.PASSWORD_FIELD, _password())
    # Rapid double-tap
    login.tap(login.SIGN_IN_BUTTON)
    try:
        login.tap(login.SIGN_IN_BUTTON, timeout=1)
    except Exception:
        # Second tap may fail because the button is already gone — that's fine.
        pass
    assert HomePage(driver).is_home_visible(timeout=30), (
        "Double-tap should still result in a successful single login"
    )
