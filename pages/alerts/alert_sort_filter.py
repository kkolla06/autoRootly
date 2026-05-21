from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class AlertSortSheet(BasePage):
    """The Sort bottom sheet on the Alerts list.

    Options: Most Recent (default) / Most Urgent. Single-select.
    Locators confirmed by rootly-alerts_sort_sheet.xml.
    """

    HEADER = ("accessibility id", "Sort")
    MOST_RECENT = ("accessibility id", "Most Recent")
    MOST_URGENT = ("accessibility id", "Most Urgent")

    OPTIONS = ("Most Recent", "Most Urgent")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def select(self, option):
        if option not in self.OPTIONS:
            raise ValueError(f"Sort option must be one of {self.OPTIONS}, got {option!r}")
        self.tap(("accessibility id", option))

    def dismiss(self):
        self.swipe_down(self.HEADER)
        self.wait_for_gone(self.HEADER, timeout=5)


class AlertViewsSheet(BasePage):
    """The Views bottom sheet on the Alerts list.

    Pulls saved views from Rootly Web. Empty state in the demo account.
    TODO: locators need raw_ios_xml/MISSING_XMLS.md (#14).
    """

    HEADER = ("accessibility id", "Views")
    EMPTY_COPY = (
        AppiumBy.IOS_PREDICATE,
        "label CONTAINS[c] 'Choose a saved view from Rootly Web'",
    )

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def is_empty(self, timeout=5):
        return self.is_visible(self.EMPTY_COPY, timeout)


class AlertStatusSheet(BasePage):
    """The Status filter sheet on the Alerts list.

    Multi-select checkboxes for: Triggered / Acknowledged / Resolved / Deferred.
    Locators confirmed by rootly-alerts_status_sheet.xml.
    """

    HEADER = ("accessibility id", "Status")
    TRIGGERED = ("accessibility id", "Triggered")
    ACKNOWLEDGED = ("accessibility id", "Acknowledged")
    RESOLVED = ("accessibility id", "Resolved")
    DEFERRED = ("accessibility id", "Deferred")

    OPTIONS = ("Triggered", "Acknowledged", "Resolved", "Deferred")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def toggle(self, option):
        if option not in self.OPTIONS:
            raise ValueError(f"Status option must be one of {self.OPTIONS}, got {option!r}")
        self.tap(("accessibility id", option))

    def dismiss(self):
        self.swipe_down(self.HEADER)
        self.wait_for_gone(self.HEADER, timeout=5)


class AlertOwnershipSheet(BasePage):
    """The Ownership filter sheet on the Alerts list.

    Single-select radio for: All alerts / My Team's alerts / My alerts.
    Locators confirmed by rootly-alerts_ownership_sheet.xml.
    """

    HEADER = ("accessibility id", "Ownership")
    ALL_ALERTS = ("accessibility id", "All alerts")
    MY_TEAMS_ALERTS = ("accessibility id", "My Team's alerts")
    MY_ALERTS = ("accessibility id", "My alerts")

    OPTIONS = ("All alerts", "My Team's alerts", "My alerts")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def select(self, option):
        if option not in self.OPTIONS:
            raise ValueError(f"Ownership option must be one of {self.OPTIONS}, got {option!r}")
        self.tap(("accessibility id", option))

    def dismiss(self):
        self.swipe_down(self.HEADER)
        self.wait_for_gone(self.HEADER, timeout=5)
