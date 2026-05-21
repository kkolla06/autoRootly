from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class HomePage(BasePage):
    """Home dashboard.

    Two visual states from the walkthrough recording:
      1. Normal — black header with on-call status + MY ACTIVITY widgets.
      2. Paged  — red header reading "You've been paged" with a preview card
                  for the active alert and a 'View Alert' button.
    """

    # Bottom nav — confirmed from rootly-home.xml
    HOME_TAB = ("accessibility id", "nav_home")
    INCIDENTS_TAB = ("accessibility id", "nav_incident")
    ALERTS_TAB = ("accessibility id", "nav_alerts")
    SHIFTS_TAB = ("accessibility id", "nav_schedules")
    MENU_TOGGLE = ("accessibility id", "nav_menu_toggle")

    # Header avatar
    SETTINGS_BUTTON = ("accessibility id", "settings_avatar_key")

    # Normal-state status header — element name uses a right single quote (U+2019)
    # in the live app, so exact == match fails; CONTAINS is encoding-safe.
    ONCALL_STATUS = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeOther' AND name CONTAINS[c] 'on-call'",
    )

    # MY ACTIVITY widgets
    MY_ACTIVITY_HEADER = ("accessibility id", "MY ACTIVITY")
    COVERAGE_REQUESTS = ("accessibility id", "coverage_requests")
    ONGOING_ALERTS = ("accessibility id", "ongoing_alerts")
    ONGOING_INCIDENTS = ("accessibility id", "ongoing_incidents")

    # MY PERFORMANCE
    MY_PERFORMANCE_HEADER = ("accessibility id", "MY PERFORMANCE")
    TIME_TO_ACK = (
        AppiumBy.IOS_PREDICATE,
        "label BEGINSWITH 'Time to ack'",
    )
    TIME_TO_RESOLVE = (
        AppiumBy.IOS_PREDICATE,
        "label BEGINSWITH 'Time to resolve'",
    )

    # Paged-home state — locators TODO confirm via raw_ios_xml/MISSING_XMLS.md (#12).
    # Until then we match on the visible header text (recording shows the
    # header reads exactly "You've been paged") and on the View Alert button.
    PAGED_BANNER = (
        AppiumBy.IOS_PREDICATE,
        "name == \"You've been paged\" OR label == \"You've been paged\"",
    )
    VIEW_ALERT_BUTTON = (
        AppiumBy.IOS_PREDICATE,
        "(type == 'XCUIElementTypeButton' OR type == 'XCUIElementTypeStaticText') "
        "AND name == 'View Alert'",
    )
    # The paged alert preview card carries the alert id (e.g. "#fQ8W5w") as
    # the leading text inside the banner.
    PAGED_ALERT_ID = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND name BEGINSWITH '#'",
    )

    # Home indicator used by the conftest.login fixture.
    # SETTINGS_BUTTON is a structural header element — no data fetch needed,
    # appears as soon as the home screen mounts. ONGOING_INCIDENTS requires a
    # server round-trip and was causing spurious re-logins on slow starts.
    HOME_INDICATOR = SETTINGS_BUTTON

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #

    def go_home(self):
        self.tap(self.HOME_TAB)

    def go_to_incidents(self):
        self.tap(self.INCIDENTS_TAB)

    def go_to_alerts(self):
        self.tap(self.ALERTS_TAB)

    def go_to_shifts(self):
        self.tap(self.SHIFTS_TAB)

    def open_menu(self):
        """Tap the '+' / Menu toggle on the bottom nav. Opens the Create menu."""
        self.tap(self.MENU_TOGGLE)

    def go_to_settings(self):
        self.tap(self.SETTINGS_BUTTON)

    # ------------------------------------------------------------------ #
    # State queries
    # ------------------------------------------------------------------ #

    def is_home_visible(self, timeout=10):
        return self.is_visible(self.HOME_INDICATOR, timeout)

    def is_paged(self, timeout=3):
        """True when the red 'You've been paged' state is displayed."""
        return self.is_visible(self.PAGED_BANNER, timeout)

    def get_oncall_status(self):
        name = self.find(self.ONCALL_STATUS).get_attribute("name")
        return name.replace("’", "'")

    def get_paged_alert_id(self):
        """Returns the alert id shown in the paged banner (e.g. '#fQ8W5w')."""
        return self.find(self.PAGED_ALERT_ID).text

    def tap_view_alert(self):
        self.tap(self.VIEW_ALERT_BUTTON)

    def get_ongoing_alerts_count(self):
        """Best-effort parse of 'Ongoing Alerts <n>' from the widget label."""
        label = self.find(self.ONGOING_ALERTS).get_attribute("label")
        # label format: 'Ongoing Alerts\n<n>' or similar
        for token in label.replace("\n", " ").split():
            if token.isdigit():
                return int(token)
        return None

    def has_all_widgets(self):
        """All MY ACTIVITY widgets and both MY PERFORMANCE cards visible."""
        return all(
            self.is_visible(loc, timeout=5)
            for loc in (
                self.COVERAGE_REQUESTS,
                self.ONGOING_ALERTS,
                self.ONGOING_INCIDENTS,
                self.TIME_TO_ACK,
                self.TIME_TO_RESOLVE,
            )
        )

    def has_bottom_nav(self):
        return all(
            self.is_visible(loc, timeout=3)
            for loc in (
                self.HOME_TAB,
                self.ALERTS_TAB,
                self.INCIDENTS_TAB,
                self.SHIFTS_TAB,
                self.MENU_TOGGLE,
            )
        )
