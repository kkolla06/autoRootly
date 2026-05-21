from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from pages.base_page import BasePage


class AlertDetailPage(BasePage):
    """The Alert detail screen — Details / Timeline / Payload tabs.

    Bottom action surface is state-dependent (per walkthrough recording):
      Triggered    → "Slide to ack"     (drag gesture)
      Acknowledged → "Slide to resolve" (drag gesture)
      Resolved     → "Escalate"         (tap button)

    The + button alongside the slider opens an action menu with state-dependent
    items (Escalate / Add note / Mark as noise / Create Incident / Share — see
    AlertActionMenu in alert_action_menu.py once captured).
    """

    # Tabs (confirmed in rootly-alert_details.xml)
    DETAILS_TAB = ("accessibility id", "alert_details_tab_detail")
    TIMELINE_TAB = ("accessibility id", "alert_details_tab_timeline")
    PAYLOAD_TAB = ("accessibility id", "alert_details_tab_payload")

    # Cards on Details tab
    TITLE_CARD = ("accessibility id", "alert_detail_card_title")
    RESPONDERS_CARD = ("accessibility id", "alert_detail_card_responders")
    LABELS_CARD = ("accessibility id", "alert_detail_card_labels")
    RELATED_INCIDENTS_CARD = (
        "accessibility id",
        "alert_detail_card_related_incidents",
    )

    # Header
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

    # Bottom action surface — state-dependent:
    #   Triggered    → slide_button (StaticText, label="Slide to ack")    at x=43, y=750
    #   Acknowledged → slide_button (Image,     label="Slide to resolve") at x=43, y=750
    #   Resolved     → shared_bottom_bar_button (Escalate button)
    # Confirmed by rootly-alert_detail_triggered/acknowledged/resolved.xml.
    BOTTOM_BAR = ("accessibility id", "shared_bottom_bar_button")
    SLIDE_BUTTON = ("accessibility id", "slide_button")   # stable target for the slide gesture
    SLIDE_TO_ACK = (AppiumBy.IOS_PREDICATE, "label CONTAINS[c] 'Slide to ack'")       # state assertion
    SLIDE_TO_RESOLVE = (AppiumBy.IOS_PREDICATE, "label CONTAINS[c] 'Slide to resolve'")  # state assertion
    ESCALATE_BUTTON = ("accessibility id", "Escalate")

    # + action menu trigger — Triggered and Resolved share the same xpath;
    # Acknowledged has a second XCUIElementTypeImage at the same path.
    ACTION_MENU_BUTTON = (
        AppiumBy.XPATH,
        "//XCUIElementTypeWindow/XCUIElementTypeOther/XCUIElementTypeOther"
        "/XCUIElementTypeOther/XCUIElementTypeOther"
        "/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]"
        "/XCUIElementTypeOther[2]/XCUIElementTypeImage",
    )
    ACTION_MENU_BUTTON_ACKED = (
        AppiumBy.XPATH,
        "//XCUIElementTypeWindow/XCUIElementTypeOther/XCUIElementTypeOther"
        "/XCUIElementTypeOther/XCUIElementTypeOther"
        "/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]"
        "/XCUIElementTypeOther[2]/XCUIElementTypeImage[2]",
    )

    # "Noise" badge — secondary label that can appear alongside a status chip
    # (e.g. Resolved + Noise). Confirmed from rootly-alert_detail_noise.xml.
    # NOT a status; get_status() is unaffected because STATUS_LABEL predicate
    # does not include "Noise".
    NOISE_BADGE = ("accessibility id", "Noise")

    VALID_STATUSES = ("Triggered", "Acknowledged", "Resolved", "Deferred")

    # ------------------------------------------------------------------ #

    def tap_back(self):
        self.tap(self.ALERT_ID)

    def is_detail_visible(self, timeout=10):
        return self.is_visible(self.DETAILS_TAB, timeout)

    def get_status(self):
        return self.find(self.STATUS_LABEL).text

    def get_severity(self):
        return self.find(self.SEVERITY_LABEL).text

    def get_alert_id(self):
        """Returns the leading-# alert id from the header (e.g. '#fQ8W5w')."""
        return self.find(self.ALERT_ID).text

    def has_severity_badge(self, timeout=5):
        return self.is_visible(self.SEVERITY_LABEL, timeout)

    def has_noise_badge(self, timeout=5):
        return self.is_visible(self.NOISE_BADGE, timeout)

    def timeline_has_event(self, event_type, timeout=10):
        """True when a timeline card of `event_type` (e.g. 'note') is visible.

        Cards are named alert_timeline_card_event_N with value=event_type.
        Confirmed in rootly-alert_detail_timeline.xml.
        """
        locator = (
            AppiumBy.IOS_PREDICATE,
            f"name BEGINSWITH 'alert_timeline_card_event' AND value == '{event_type}'",
        )
        return self.is_visible(locator, timeout)

    def all_cards_visible(self):
        return all(
            self.is_visible(loc, timeout=5)
            for loc in (
                self.TITLE_CARD,
                self.RESPONDERS_CARD,
                self.LABELS_CARD,
                self.RELATED_INCIDENTS_CARD,
            )
        )

    def tap_details_tab(self):
        self.tap(self.DETAILS_TAB)

    def tap_timeline_tab(self):
        self.tap(self.TIMELINE_TAB)

    def tap_payload_tab(self):
        self.tap(self.PAYLOAD_TAB)

    # -- State transitions ---------------------------------------------- #

    def _slide_full_track(self):
        """Slide across the full track width (x=50→350, y=773).

        SLIDE_BUTTON rect is only 67px wide (the handle), but the track
        ScrollView is 316px wide (x=37–353). Sliding handle-width only never
        completes the gesture. Hardcoded from rootly-alert_detail_triggered.xml.
        """
        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(50, 773)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.6)
        actions.pointer_action.move_to_location(350, 773)
        actions.pointer_action.release()
        actions.perform()

    def slide_to_ack(self):
        self._slide_full_track()

    def slide_to_resolve(self):
        self.wait_for_visible(self.SLIDE_TO_RESOLVE, timeout=5)
        self._slide_full_track()

    def tap_escalate_button(self):
        """Tap the Escalate button — only present when the alert is Resolved."""
        self.tap(self.ESCALATE_BUTTON)

    def open_action_menu(self):
        """Tap the + button to open the action menu.

        Coordinates from Appium Inspector per state:
          Triggered / Acknowledged → x=330, y=770
          Resolved                 → x=260, y=770  (Escalate button shifts the layout)
        """
        x = 260 if self.is_visible(self.ESCALATE_BUTTON, timeout=2) else 330
        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(x, 770)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.05)
        actions.pointer_action.release()
        actions.perform()


    def dismiss_sheet_alert_ack_menu(self):
        """Tap the + button to open the action menu.

        Coordinates from Appium Inspector per state:
          x=180, y=400
        """
        x = 340
        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(x, 770)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.05)
        actions.pointer_action.release()
        actions.perform()