from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class IncidentListPage(BasePage):
    # Confirmed from rootly-incidents.xml
    INCIDENTS_HEADER = ("accessibility id", "Incidents")
    FIRST_INCIDENT = ("accessibility id", "incident_0")

    # Confirmed from rootly-incidents.xml: chips are StaticText, not Button.
    # name="Status\nAll" (or "Status\n<selected>" after filtering).
    STATUS_FILTER = (
        AppiumBy.IOS_PREDICATE,
        "name BEGINSWITH 'Status' AND type == 'XCUIElementTypeStaticText'",
    )
    OWNERSHIP_FILTER = (
        AppiumBy.IOS_PREDICATE,
        "name BEGINSWITH 'Ownership' AND type == 'XCUIElementTypeStaticText'",
    )

    SETTINGS_AVATAR = ("accessibility id", "settings_avatar")

    def open_settings(self):
        self.tap(self.SETTINGS_AVATAR)

    def is_list_visible(self) -> bool:
        return self.is_visible(self.INCIDENTS_HEADER)

    def open_first_incident(self):
        self.tap(self.FIRST_INCIDENT)

    def open_incident_at(self, index: int):
        locator = ("accessibility id", f"incident_{index}")
        self.tap(locator)

    def find_incident_by_title(self, title: str) -> bool:
        locator = (
            AppiumBy.IOS_PREDICATE,
            f"type == 'XCUIElementTypeButton' AND label == '{title}'",
        )
        return self.is_visible(locator)

    def tap_status_filter(self):
        self.tap(self.STATUS_FILTER)

    def tap_ownership_filter(self):
        self.tap(self.OWNERSHIP_FILTER)

    def has_any_incident(self) -> bool:
        return self.is_visible(self.FIRST_INCIDENT, timeout=5)

    def row_severity_visible(self, index: int = 0) -> bool:
        """Asserts a SEV badge (SEV0..SEV5) is rendered in the row."""
        loc = (
            AppiumBy.IOS_PREDICATE,
            "type == 'XCUIElementTypeImage' AND name MATCHES 'SEV[0-5]'",
        )
        return self.is_visible(loc, timeout=5)
