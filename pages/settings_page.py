from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class SettingsPage(BasePage):
    # Confirmed from rootly-settings.xml
    HEADER = ("accessibility id", "Settings")

    # Profile card
    USER_AVATAR = ("accessibility id", "KK")
    # Name and email are dynamic — match by predicate at runtime instead of hardcoding.
    NAME_LABEL = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND name MATCHES '[A-Z][a-z]+ [A-Z][a-z]+'",
    )
    EMAIL_LABEL = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND name CONTAINS '@'",
    )

    # Menu items (all confirmed)
    ORGANIZATION = ("accessibility id", "settings_organization")
    MEMBERS = ("accessibility id", "settings_members")
    ON_CALL_NOTIFICATIONS = ("accessibility id", "settings_on_call_notifications")
    APPEARANCE = ("accessibility id", "settings_appearance")
    LANGUAGE = ("accessibility id", "settings_language")
    EMAIL_SUPPORT = ("accessibility id", "settings_email_support")
    ABOUT = ("accessibility id", "settings_about")
    TROUBLESHOOTING = ("accessibility id", "settings_troubleshooting")
    NOTIFICATION_SETTINGS = ("accessibility id", "settings_notification_settings")
    CLEAR_CACHE_AND_DATA = ("accessibility id", "settings_clear_cache_and_data")
    UPDATE_CONTACT_CARD = ("accessibility id", "settings_update_contact_card")
    LOG_OUT = ("accessibility id", "settings_log_out")

    # On-Call Notifications sub-screen
    ON_CALL_NOTIFICATIONS_HEADER = ("accessibility id", "On-Call Notifications")

    # About sub-screen
    ABOUT_HEADER = ("accessibility id", "About")
    ABOUT_DEVICE_NAME = ("accessibility id", "settings_device_name")
    ABOUT_SYSTEM_STATUS = ("accessibility id", "settings_about_rootly_system_status")
    ABOUT_PRIVACY_POLICY = ("accessibility id", "settings_about_privacy_policy")
    ABOUT_TERMS_OF_USE = ("accessibility id", "settings_about_terms_of_use")
    ABOUT_VERSION = ("accessibility id", "settings_about_version")

    # Appearance sub-screen
    APPEARANCE_HEADER = ("accessibility id", "Appearance")
    APPEARANCE_SYSTEM = ("accessibility id", "settings_appearance_system")
    APPEARANCE_LIGHT = ("accessibility id", "settings_appearance_light")
    APPEARANCE_DARK = ("accessibility id", "settings_appearance_dark")

    # Safari identifiers for About-screen web redirects.
    # System Status: address bar is visible → check domain via TabBarItemTitle.
    # Privacy Policy / Terms of Use: bar is hidden → check in-page H1 instead.
    SAFARI_ADDRESS_BAR = ("accessibility id", "TabBarItemTitle")
    SAFARI_PRIVACY_POLICY_TITLE = ("accessibility id", "Privacy Policy")
    SAFARI_TERMS_OF_USE_TITLE = ("accessibility id", "Terms of Use")

    # iOS Settings → Rootly notification screen (opened via Notification Settings row)
    IOS_NOTIF_SETTINGS_TITLE = ("accessibility id", "Rootly")
    IOS_NOTIF_SETTINGS_ALLOW_TOGGLE = ("accessibility id", "Allow Notifications")

    # Back button — leftmost button in header (no name in XML)
    BACK_BUTTON = (
        AppiumBy.IOS_CLASS_CHAIN,
        "**/XCUIElementTypeButton[1]",
    )

    # Confirmation dialog buttons for Clear Cache & Data — names are best-guess
    # based on iOS conventions; verify against captured XML when bug is observed.
    CONFIRM_CLEAR_BUTTON = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeButton' AND "
        "(name == 'Clear' OR name == 'Confirm' OR label CONTAINS[c] 'clear')",
    )
    CANCEL_CLEAR_BUTTON = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeButton' AND name == 'Cancel'",
    )

    # Rows exercised by the combined sanity-check test.
    # Excluded — each has a dedicated test: APPEARANCE, ABOUT.
    # Excluded — redirect out of app: EMAIL_SUPPORT, UPDATE_CONTACT_CARD.
    TAPPABLE_ROWS = (
        ORGANIZATION,
        MEMBERS,
        LANGUAGE,
        TROUBLESHOOTING,
    )

    def is_visible(self, locator=None, timeout: int = 5) -> bool:
        return super().is_visible(locator if locator is not None else self.HEADER, timeout)

    def back(self):
        self.tap(self.BACK_BUTTON)

    def tap_clear_cache_and_data(self):
        self.tap(self.CLEAR_CACHE_AND_DATA)

    def confirm_clear_cache(self):
        self.tap(self.CONFIRM_CLEAR_BUTTON)

    def cancel_clear_cache(self):
        self.tap(self.CANCEL_CLEAR_BUTTON)

    def tap_log_out(self):
        self.tap(self.LOG_OUT)

    def tap_on_call_notifications(self):
        self.tap(self.ON_CALL_NOTIFICATIONS)

    def tap_notification_settings(self):
        self.tap(self.NOTIFICATION_SETTINGS)

    def is_ios_notification_settings_visible(self, timeout: int = 10) -> bool:
        return (
            self.is_visible(self.IOS_NOTIF_SETTINGS_TITLE, timeout)
            and self.is_visible(self.IOS_NOTIF_SETTINGS_ALLOW_TOGGLE, timeout)
        )

    def tap_appearance(self):
        self.tap(self.APPEARANCE)

    def is_appearance_visible(self, timeout: int = 5) -> bool:
        return self.is_visible(self.APPEARANCE_HEADER, timeout)

    def tap_appearance_light(self):
        self.tap(self.APPEARANCE_LIGHT)

    def tap_appearance_dark(self):
        self.tap(self.APPEARANCE_DARK)

    def tap_appearance_system(self):
        self.tap(self.APPEARANCE_SYSTEM)

    def tap_about(self):
        self.tap(self.ABOUT)

    def is_safari_at(self, expected_domain: str, timeout: int = 10) -> bool:
        try:
            el = self.find_visible(self.SAFARI_ADDRESS_BAR, timeout)
            return expected_domain in (el.get_attribute("value") or "")
        except Exception:
            return False

    def is_about_visible(self, timeout: int = 5) -> bool:
        return self.is_visible(self.ABOUT_HEADER, timeout)

    def get_app_version(self) -> str:
        """Returns the bare version string (e.g. '2.13.1') from the About sub-screen."""
        label = self.find(self.ABOUT_VERSION).get_attribute("value")
        # value is "Version\nVersion\n2.13.1"
        return label.split("\n")[-1].strip()

    def has_profile_info(self) -> bool:
        return (
            self.is_visible(self.NAME_LABEL, timeout=5)
            and self.is_visible(self.EMAIL_LABEL, timeout=5)
            and self.is_visible(self.ORGANIZATION, timeout=5)
            and self.is_visible(self.ABOUT, timeout=5)
        )
