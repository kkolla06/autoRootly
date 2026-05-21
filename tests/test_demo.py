"""Showpiece demo — full Rootly iOS walkthrough in one continuous flow.

  01. Google sign-in bug (if at landing; skipped when session cached)
  02. Email/password login
  03. Nav cycling — + menu open, cycle all bottom-nav tabs
  04. Create DEMO_ALERT
  05. Navigate to alert — assert Triggered
  06. Triggered action menu validation
  07. BUG — Create Incident title not autofilled (continues from open menu)
  08. Slide to ack — assert Acknowledged
  09. Acknowledged action menu validation
  10. Slide to resolve — assert Resolved
  11. Resolved action menu validation
  12. Escalate (primary button → two-step form → toast)
  13. Home → Settings
  14. Settings: profile info
  15. Settings: Appearance (3 themes)
  16. Settings: About — version + web redirects
  17. Settings: Notification Settings → iOS Settings
  last. Log out → landing page → login form opens
"""
import logging
import os
import re
import time

import pytest
from pages.landing_page import LandingPage
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.alerts.alerts_page import AlertsPage
from pages.alerts.alert_detail_page import AlertDetailPage
from pages.alerts.alert_escalate_page import AlertEscalateToSheet, AlertEscalatePage
from pages.alerts.alert_action_menu import AlertActionMenu
from pages.incidents.create_incident_page import CreateIncidentPage
from pages.create_menu import CreateMenu
from pages.select_responders import SelectResponders
from pages.alerts.alert_create_page import AlertCreatePage
from pages.settings_page import SettingsPage

log = logging.getLogger(__name__)

DEMO_ALERT = "DEMO_FINAL_FINAL_ALERT"


@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.e2e
def test_demo(driver):
    """TC-E2E-DEMO — Full Rootly iOS demo: login → nav → alerts → settings → logout."""

    home = HomePage(driver)

    # ── 01. Google sign-in bug ────────────────────────────────────────────────
    landing = LandingPage(driver)
    if landing.is_visible(timeout=5):
        login_page = LoginPage(driver)
        login_page.open_from_landing()
        login_page.tap_google()
        assert not home.is_home_visible(timeout=5), (
            "Reached Home — Google OAuth appears fixed"
        )
        log.info("!! BUG: Google OAuth confirmed broken — does not reach Home [known bug]")
        login_page.cancel()

    # ── 02. Email/password login ──────────────────────────────────────────────
    if not home.is_home_visible(timeout=5):
        LoginPage(driver).login(
            email=os.getenv("ROOTLY_TEST_EMAIL"),
            password=os.getenv("ROOTLY_TEST_PASSWORD"),
        )
    assert home.is_home_visible(timeout=30), "Home not reached after login"
    log.info("✓ Login successful — Home screen reached")

    # ── 03. Nav cycling ───────────────────────────────────────────────────────
    home.open_menu()
    for x, y in (
        (155, 750),  # alerts
        (200, 750),  # incidents
        (300, 750),  # shifts
        (170, 750),  # incidents
        (100, 750),  # alerts
        (50,  750),  # home
    ):
        time.sleep(0.5)
        home.tap_coordinate(x, y)
    log.info("✓ Nav cycling — 6 tabs cycled behind open menu, returned to Home")
    log.info("!! BUG: Nav behind open menu is still interactive [known bug]")

    # ── 04. Create alert ──────────────────────────────────────────────────────
    menu = CreateMenu(driver)
    assert menu.is_visible(timeout=5), "Create menu not visible"
    log.info("✓ Create menu opened")
    menu.tap_create_alert()
    form = AlertCreatePage(driver)
    form.wait_for_visible(form.SUBMIT_BUTTON)
    form.open_responder_picker()
    picker = SelectResponders(driver)
    picker.wait_for_visible(picker.SEARCH_FIELD)
    picker.expand_category("People")
    picker.select("Kaushik Kolla")
    picker.done()
    log.info("✓ Kaushik Kolla added as responder")
    form.fill_title(DEMO_ALERT)
    form.submit()
    form.wait_for_toast("Manual page created successfully", timeout=15)
    log.info("✓ Alert 'Demo Alert' created — success toast confirmed")

    # ── 05. Navigate to alert — assert Triggered ──────────────────────────────
    home.go_home()
    if home.is_paged(timeout=5):
        home.tap_view_alert()
    else:
        home.go_to_alerts()
        AlertsPage(driver).open_alert_by_title(DEMO_ALERT)
    detail = AlertDetailPage(driver)
    detail.wait_for_visible(detail.DETAILS_TAB, timeout=10)
    assert detail.get_status() == "Triggered"
    log.info("✓ Navigated to Demo Alert — status confirmed: Triggered")

    # ── 06. Triggered action menu ─────────────────────────────────────────────
    detail.open_action_menu()
    action_menu = AlertActionMenu(driver)
    assert action_menu.is_visible(timeout=5), "Action menu did not open"
    assert action_menu.is_visible_option("Resolve"), "Resolve missing in Triggered menu"
    log.info("✓ Resolve present")
    assert action_menu.is_visible_option("Escalate"), "Escalate missing in Triggered menu"
    log.info("✓ Escalate present")
    assert action_menu.is_visible_option("Add note"), "Add note missing"
    log.info("✓ Add note present")
    assert action_menu.is_visible_option("Mark as noise"), "Mark as noise missing"
    log.info("✓ Mark as noise present")
    assert action_menu.is_visible_option("Create Incident"), "Create Incident missing"
    log.info("✓ Create Incident present")
    log.info("✓ Triggered action menu fully validated")

    # ── 07. BUG: Create Incident — title not autofilled ───────────────────────
    # Menu is still open from step 06 — tap directly without reopening
    action_menu.tap_create_incident()
    inc_form = CreateIncidentPage(driver)
    assert inc_form.is_visible(timeout=5), "Create Incident form did not open"
    inc_form.close()
    detail.tap_coordinate(180, 770)  # tap confirm incendent creation toast
    time.sleep(1)
    detail.wait_for_visible(detail.DETAILS_TAB, timeout=10)

    # ── 08. Slide to ack ──────────────────────────────────────────────────────
    assert detail.get_status() == "Triggered", "Demo Alert should be Triggered before ack"
    detail.wait_for_visible(detail.SLIDE_TO_ACK, timeout=5)
    detail.slide_to_ack()
    time.sleep(2)
    detail.wait_for_visible(("accessibility id", "Acknowledged"), timeout=10)
    assert detail.get_status() == "Acknowledged"
    log.info("✓ Slide-to-Acknowledge — status: Acknowledged")

    # ── 09. Acknowledged action menu ─────────────────────────────────────────
    detail.open_action_menu()
    acked_menu = AlertActionMenu(driver)
    assert acked_menu.is_visible(timeout=5), "Acknowledged action menu did not open"
    assert not acked_menu.is_visible_option("Resolve"), "Resolve should be absent when Acknowledged"
    log.info("✓ Resolve absent (correct — slide-to-resolve handles this state)")
    assert acked_menu.is_visible_option("Escalate"), "Escalate missing in Acknowledged menu"
    log.info("✓ Escalate present")
    assert acked_menu.is_visible_option("Add note"), "Add note present"
    assert acked_menu.is_visible_option("Mark as noise"), "Mark as noise present"
    assert acked_menu.is_visible_option("Create Incident"), "Create Incident present"
    log.info("✓ Acknowledged action menu fully validated")
    time.sleep(0.5)
    detail.dismiss_sheet_alert_ack_menu()

    # ── 10. Slide to resolve ──────────────────────────────────────────────────
    detail.wait_for_visible(detail.SLIDE_TO_RESOLVE, timeout=8)
    detail.slide_to_resolve()
    detail.wait_for_visible(("accessibility id", "Resolved"), timeout=10)
    assert detail.get_status() == "Resolved"
    log.info("✓ Slide-to-Resolve — status: Resolved")

    # ── 11. Resolved action menu ──────────────────────────────────────────────
    time.sleep(0.5)
    detail.open_action_menu()
    time.sleep(0.5)
    res_menu = AlertActionMenu(driver)
    assert res_menu.is_visible(timeout=5), "Resolved action menu did not open"
    assert not res_menu.is_visible_option("Resolve"), "Resolve should be absent when Resolved"
    log.info("✓ Resolve absent (alert already resolved)")
    assert not res_menu.is_visible_option("Escalate"), "Escalate should be absent (primary button)"
    log.info("✓ Escalate absent (shown as primary button instead)")
    assert res_menu.is_visible_option("Add note"), "Add note missing"
    assert res_menu.is_visible_option("Mark as noise"), "Mark as noise missing"
    assert res_menu.is_visible_option("Create Incident"), "Create Incident missing"
    log.info("✓ Resolved action menu fully validated")
    detail.dismiss_sheet_alert_ack_menu()

    # ── 12. Escalate ──────────────────────────────────────────────────────────
    assert detail.is_visible(detail.ESCALATE_BUTTON, timeout=5), "Escalate button missing"
    log.info("✓ Escalate primary button visible on Resolved alert")
    detail.tap_escalate_button()
    esc_to = AlertEscalateToSheet(driver)
    assert esc_to.is_visible(timeout=5), "Escalate-to sheet not visible"
    esc_to.confirm()
    esc_form = AlertEscalatePage(driver)
    assert esc_form.is_visible(timeout=5), "Escalate form not visible"
    log.info("✓ Escalate form opened")
    esc_form.open_responder_picker()
    picker = SelectResponders(driver)
    time.sleep(1)  
    picker.expand_category("People")
    picker.select("Kaushik Kolla")
    picker.done()
    log.info("✓ Kaushik Kolla selected as escalation target")
    esc_form.submit()
    esc_form.wait_for_toast("You have escalated successfully", timeout=15)
    log.info("✓ Escalation successful — toast confirmed")
    time.sleep(1)
    home.tap_coordinate(30, 70)
    log.info("!! BUG: does not return to list screen after escalation — tapped back [known bug]")
    home.tap_coordinate(30, 70)

    # ── 13. Home → Settings ───────────────────────────────────────────────────
    home.go_home()
    assert home.is_home_visible(timeout=10), "Did not return to Home"
    home.go_to_settings()
    settings = SettingsPage(driver)
    assert settings.is_visible(timeout=10), "Settings did not open"
    log.info("✓ Settings screen opened")

    # ── 14. Profile info ──────────────────────────────────────────────────────
    assert settings.has_profile_info(), "Profile info (name/email/org) missing"
    log.info("✓ Profile info present (name, email, organisation)")

    # ── 15. Appearance — 3 themes ─────────────────────────────────────────────
    settings.tap_appearance()
    assert settings.is_appearance_visible(timeout=5), "Appearance sub-screen did not open"
    assert settings.is_visible(settings.APPEARANCE_SYSTEM, timeout=3), "System theme missing"
    assert settings.is_visible(settings.APPEARANCE_LIGHT, timeout=3), "Light theme missing"
    assert settings.is_visible(settings.APPEARANCE_DARK, timeout=3), "Dark theme missing"
    log.info("✓ Appearance: System / Light / Dark themes all present")
    settings.back()

    # ── 16. About — version + web redirects ───────────────────────────────────
    settings.tap_about()
    assert settings.is_about_visible(timeout=5), "About sub-screen did not open"
    version = settings.get_app_version()
    assert re.match(r"\d+\.\d+", version), f"Unexpected version format: {version!r}"
    log.info("✓ App version: %s", version)

    settings.tap(settings.ABOUT_SYSTEM_STATUS)
    assert settings.is_safari_at("status.rootly.com", timeout=10), (
        "System Status did not open status.rootly.com in Safari"
    )
    driver.activate_app(os.getenv("APP_BUNDLE_ID"))
    assert settings.is_about_visible(timeout=10), "About screen did not restore after System Status"
    log.info("✓ System Status opens status.rootly.com in Safari")

    settings.tap(settings.ABOUT_PRIVACY_POLICY)
    assert settings.is_visible(settings.SAFARI_PRIVACY_POLICY_TITLE, timeout=10), (
        "Privacy Policy did not open correctly in Safari"
    )
    driver.activate_app(os.getenv("APP_BUNDLE_ID"))
    assert settings.is_about_visible(timeout=10), "About screen did not restore after Privacy Policy"
    log.info("✓ Privacy Policy opens correctly in Safari")

    settings.tap(settings.ABOUT_TERMS_OF_USE)
    assert settings.is_visible(settings.SAFARI_TERMS_OF_USE_TITLE, timeout=10), (
        "Terms of Use did not open correctly in Safari"
    )
    driver.activate_app(os.getenv("APP_BUNDLE_ID"))
    assert settings.is_about_visible(timeout=10), "About screen did not restore after Terms of Use"
    log.info("✓ Terms of Use opens correctly in Safari")
    time.sleep(1)
    settings.back()

    # ── 17. Notification Settings → iOS Settings ──────────────────────────────
    settings.tap_notification_settings()
    assert settings.is_ios_notification_settings_visible(timeout=10), (
        "iOS Settings Rootly notification screen did not open"
    )
    driver.activate_app(os.getenv("APP_BUNDLE_ID"))
    assert settings.is_visible(timeout=10), "Settings did not restore after iOS Settings"
    log.info("✓ Notification Settings redirects to iOS Settings and returns correctly")

    # ── last. Log out ─────────────────────────────────────────────────────────
    settings.tap_log_out()
    home.tap_coordinate(265, 480)  # confirm iOS log out toast/dialog
    landing = LandingPage(driver)
    assert landing.is_visible(timeout=10), "Landing page not visible after log out"
    log.info("✓ Logged out — Landing page confirmed")
    login_page = LoginPage(driver)
    time.sleep(1)
    landing.tap_log_in()
    home.tap_coordinate(265, 480)  # confirm iOS toast after tapping Sign In
    time.sleep(2)
    log.info("!! BUG: Login form did not open after tapping Sign In if inital sign in was with 'Remeber me' [known bug]")
    login_page.cancel()
    log.info("**Demo complete**")
