from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class IncidentDetailPage(BasePage):
    """Incident detail screen — Details / Alerts tabs.

    Status set confirmed from rootly-incident-status_filter.xml.
    More-menu icon (nameless XCUIElementTypeImage at x≈290, y≈770) tapped by coordinate.
    """

    # Confirmed from rootly-incident_details.xml
    DETAILS_TAB = ("accessibility id", "Details\nTab 1 of 2")
    ALERTS_TAB = ("accessibility id", "Alerts\nTab 2 of 2")
    ADD_ALERT_BUTTON = ("accessibility id", "Add related alert")

    # Severity badge image (e.g. SEV2). type==Image, name matches SEV0..SEV5.
    SEVERITY_BADGE = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeImage' AND name MATCHES 'SEV[0-5]'",
    )

    # Duration like "1h", "23m" — short StaticText near the top of the page.
    DURATION = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND "
        "(name MATCHES '[0-9]+[smhd]' OR name MATCHES '[0-9]+[smhd][0-9]+[smhd]')",
    )

    # Status confirmed from rootly-incident-status_filter.xml.
    STATUS_LABEL = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND "
        "name IN {'In-Triage','Active','Mitigated','Resolved','Closed','Cancelled'}",
    )

    # More-menu icon — no name/label in XML; confirmed at x=268,y=748,w=49,h=50.
    # Centre ~(292, 773); use tap_more_menu() which hits (290, 770).

    # No accessibility id — only identifier found via Appium Inspector.
    BACK_BUTTON = (
        AppiumBy.IOS_CLASS_CHAIN,
        "**/XCUIElementTypeWindow/XCUIElementTypeOther/XCUIElementTypeOther"
        "/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[2]"
        "/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]"
        "/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]",
    )

    ACKNOWLEDGE_BUTTON = ("accessibility id", "Acknowledge")
    RESOLVE_BUTTON = ("accessibility id", "Resolve")

    VALID_STATUSES = ("In-Triage", "Active", "Mitigated", "Resolved", "Closed", "Cancelled")

    def tap_more_menu(self):
        """Tap the nameless more-menu icon at the bottom-right of the detail screen."""
        self.tap_coordinate(290, 770)

    def tap_back(self):
        self.tap(self.BACK_BUTTON)

    def is_detail_visible(self):
        return self.is_visible(self.DETAILS_TAB)

    def get_status(self):
        return self.find(self.STATUS_LABEL).text

    def has_severity_badge(self):
        return self.is_visible(self.SEVERITY_BADGE, timeout=5)

    def has_duration(self):
        return self.is_visible(self.DURATION, timeout=5)

    def tap_alerts_tab(self):
        self.tap(self.ALERTS_TAB)

    def tap_details_tab(self):
        self.tap(self.DETAILS_TAB)

    def acknowledge(self):
        self.tap(self.ACKNOWLEDGE_BUTTON)

    def resolve(self):
        self.tap(self.RESOLVE_BUTTON)
