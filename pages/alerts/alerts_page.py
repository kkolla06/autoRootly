from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from pages.alerts.alert_sort_filter import AlertStatusSheet, AlertOwnershipSheet


class AlertsPage(BasePage):
    """The Alerts list screen (bottom-nav Alerts tab).

    Detail-screen concerns are now in `pages/alerts/alert_detail_page.py` —
    this class only models the list + its 4-button filter bar.

    Filter bar from left to right (per the walkthrough recording):
      1. Sort        (icon, no accessibility id — class-chain fallback)
      2. Views       (icon, no accessibility id — class-chain fallback)
      3. Status      (button, label "Status <current>") — multi-select sheet
      4. Ownership   (button, label "Ownership <current>") — single-select sheet
    """

    # Header
    ALERTS_HEADER = ("accessibility id", "Alerts")
    SETTINGS_AVATAR = ("accessibility id", "KK")

    # Filter bar
    # Sort + Views are anonymous icons (XCUIElementTypeImage with no `name`).
    # Sit just left of the Status filter; located by class chain index until
    # accessibility IDs are added — see raw_ios_xml/MISSING_XMLS.md (#13, #14).
    SORT_BUTTON = (
        AppiumBy.IOS_CLASS_CHAIN,
        "**/XCUIElementTypeImage[`visible == 1 AND name == nil`][1]",
    )
    VIEWS_BUTTON = (
        AppiumBy.IOS_CLASS_CHAIN,
        "**/XCUIElementTypeImage[`visible == 1 AND name == nil`][2]",
    )
    STATUS_FILTER = ("accessibility id", "alert_status_filter")
    OWNERSHIP_FILTER = ("accessibility id", "alert_ownership_filter")

    # The filter button label changes as the user picks options (e.g.
    # "Status All" → "Status Triggered, Acknowledged"). The sub-label
    # accessibility IDs let us read the current selection without parsing.
    STATUS_FILTER_VALUE = ("accessibility id", "alert_status_filter_all")
    OWNERSHIP_FILTER_VALUE = ("accessibility id", "alert_ownership_filter_all")

    # List rows
    FIRST_ALERT = ("accessibility id", "alert_0")

    # Reference: alert state machine confirmed from the walkthrough recording.
    # Status pill in row + detail header uses these exact labels.
    VALID_STATUSES = ("Triggered", "Acknowledged", "Resolved", "Deferred")
    VALID_SEVERITIES = ("Critical", "High", "Medium", "Low")

    def open_settings(self):
        self.tap(self.SETTINGS_AVATAR)

    def is_alerts_list_visible(self, timeout=5):
        return self.is_visible(self.ALERTS_HEADER, timeout) or self.is_visible(
            self.STATUS_FILTER, timeout
        )

    def open_first_alert(self):
        self.tap(self.FIRST_ALERT)

    def open_alert_at(self, index):
        self.tap(("accessibility id", f"alert_{index}"))

    def reset_filters(self):
        """Reset Status to All and Ownership to All alerts if either is narrowed.

        Filter state persists across app restarts (stored in device local
        storage). STATUS_FILTER_VALUE is only visible when all 4 statuses are
        shown; OWNERSHIP_FILTER_VALUE is only visible when ownership is All.
        Each status option exposes value="1" (selected) or "0" (not selected).
        """
        if not self.is_visible(self.STATUS_FILTER_VALUE, timeout=2):
            self.tap_status_filter()
            for opt in AlertStatusSheet.OPTIONS:
                el = self.find(("accessibility id", opt))
                if el.get_attribute("value") != "1":
                    el.click()
            AlertStatusSheet(self.driver).dismiss()

        if not self.is_visible(self.OWNERSHIP_FILTER_VALUE, timeout=2):
            self.tap_ownership_filter()
            AlertOwnershipSheet(self.driver).select("All alerts")
            AlertOwnershipSheet(self.driver).dismiss()

    def open_alert_by_title(self, title):
        """Tap the first visible alert row whose label contains `title`."""
        self.tap((AppiumBy.IOS_PREDICATE, f"label CONTAINS '{title}'"))

    def has_any_alert(self, timeout=5):
        return self.is_visible(self.FIRST_ALERT, timeout)

    def tap_sort(self):
        self.tap(self.SORT_BUTTON)

    def tap_views(self):
        self.tap(self.VIEWS_BUTTON)

    def tap_status_filter(self):
        self.tap(self.STATUS_FILTER)

    def tap_ownership_filter(self):
        self.tap(self.OWNERSHIP_FILTER)
        # The ownership sheet can fail to open if the alerts list is still
        # refreshing after a status filter change (layout blocks the tap).
        # Retry once if the sheet header doesn't appear within 2 seconds.
        if not self.is_visible(("accessibility id", "Ownership"), timeout=2):
            self.tap(self.OWNERSHIP_FILTER)

    def get_status_filter_value(self):
        """Returns the current Status chip text (e.g. 'All' or 'Triggered')."""
        return self.find(self.STATUS_FILTER_VALUE).text

    def get_ownership_filter_value(self):
        """Returns the current Ownership chip text (e.g. 'All alerts')."""
        return self.find(self.OWNERSHIP_FILTER_VALUE).text

    # ------------------------------------------------------------------ #
    # Backwards-compat shims for tests that still expect detail locators
    # on the AlertsPage class. New tests should import AlertDetailPage.
    # ------------------------------------------------------------------ #

    DETAILS_TAB = ("accessibility id", "alert_details_tab_detail")
    TIMELINE_TAB = ("accessibility id", "alert_details_tab_timeline")
    PAYLOAD_TAB = ("accessibility id", "alert_details_tab_payload")
    ESCALATE_BUTTON = ("accessibility id", "Escalate")

    ALERT_TITLE_CARD = ("accessibility id", "alert_detail_card_title")
    ALERT_RESPONDERS_CARD = ("accessibility id", "alert_detail_card_responders")
    ALERT_LABELS_CARD = ("accessibility id", "alert_detail_card_labels")
    ALERT_RELATED_INCIDENTS_CARD = (
        "accessibility id",
        "alert_detail_card_related_incidents",
    )

    ALERT_ID = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND name BEGINSWITH '#'",
    )
    SEVERITY_LABEL = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND name IN "
        "{'Critical','High','Medium','Low'}",
    )
    STATUS_LABEL = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND name IN "
        "{'Triggered','Acknowledged','Resolved','Deferred'}",
    )

    def is_detail_visible(self):
        return self.is_visible(self.DETAILS_TAB)

    def tap_details_tab(self):
        self.tap(self.DETAILS_TAB)

    def tap_timeline_tab(self):
        self.tap(self.TIMELINE_TAB)

    def tap_payload_tab(self):
        self.tap(self.PAYLOAD_TAB)

    def tap_escalate(self):
        self.tap(self.ESCALATE_BUTTON)

    def get_severity(self):
        return self.find(self.SEVERITY_LABEL).text

    def get_status(self):
        return self.find(self.STATUS_LABEL).text

    def detail_cards_visible(self):
        return all(
            self.is_visible(loc, timeout=5)
            for loc in (
                self.ALERT_TITLE_CARD,
                self.ALERT_RESPONDERS_CARD,
                self.ALERT_LABELS_CARD,
                self.ALERT_RELATED_INCIDENTS_CARD,
            )
        )
