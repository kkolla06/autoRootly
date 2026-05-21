from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from pages.base_page import BasePage


class AlertEscalateToSheet(BasePage):
    """Intermediate 'Escalate to' bottom sheet that appears after tapping Escalate.

    Confirmed from rootly-alert_escalate_to_sheet.xml. User picks the
    escalation target (default already selected: 'A different Escalation
    Policy / User') then taps Confirm to open the full Escalate form.
    """

    HEADER = ("accessibility id", "Escalate to")
    OPTION = ("accessibility id", "A different Escalation Policy / User")
    CONFIRM_BUTTON = ("accessibility id", "Confirm")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def confirm(self):
        self.tap(self.CONFIRM_BUTTON)


class UrgencySheet(BasePage):
    """Urgency picker sheet shared by Create Alert and Escalate forms.

    Confirmed from rootly-alert_create_urgency_open.xml.
    Header 'Select Urgency'. Options: High (default selected), Medium, Low.
    """

    HEADER = ("accessibility id", "Select Urgency")
    HIGH = ("accessibility id", "High")
    MEDIUM = ("accessibility id", "Medium")
    LOW = ("accessibility id", "Low")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def select(self, level):
        mapping = {"High": self.HIGH, "Medium": self.MEDIUM, "Low": self.LOW}
        if level not in mapping:
            raise ValueError(f"Unknown urgency level {level!r}")
        self.tap(mapping[level])


class AlertEscalatePage(BasePage):
    """The Escalate form modal.

    Two-step entry: tap Escalate -> AlertEscalateToSheet (pick target +
    Confirm) -> this form. Confirmed from rootly-alert_escalate_form.xml.

    Copy reads: "You're escalating the alert <title>. This will stop all
    in-progress paging and immediately notify the selected recipients."

    Required: Who do you want to notify? (opens Select Responders sheet) +
    Urgency (opens UrgencySheet). Optional: Note (free text).

    CLOSE_BUTTON confirmed (XCUIElementTypeButton name="Close" top-left).
    SUBMIT_CONTAINER = "manual_page_create_button" avoids name collision with
    the "Escalate" header element.
    """

    HEADER = ("accessibility id", "Escalate")
    CLOSE_BUTTON = ("accessibility id", "Close")

    # "Who to notify" label is visible=false in XML — tap via predicate on
    # the label text so Appium hits the tappable parent container.
    NOTIFY_DROPDOWN = (
        AppiumBy.IOS_PREDICATE,
        "label CONTAINS 'Who do you want to notify'",
    )
    URGENCY_DROPDOWN = ("accessibility id", "Urgency *")
    NOTE_FIELD = ("accessibility id", "Note")

    # Both present in XML: container "manual_page_create_button" + Button
    # "Escalate". Use container to avoid collision with the HEADER element.
    SUBMIT_CONTAINER = ("accessibility id", "manual_page_create_button")

    BODY_COPY = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND "
        "label BEGINSWITH \"You're escalating the alert\"",
    )

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def get_body_copy(self):
        return self.find(self.BODY_COPY).text

    def open_responder_picker(self):
        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(180, 240)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.05)
        actions.pointer_action.release()
        actions.perform()

    def open_urgency_picker(self):
        self.tap(self.URGENCY_DROPDOWN)

    def fill_note(self, text):
        self.type_text(self.NOTE_FIELD, text)

    def submit(self):
        self.tap(self.SUBMIT_CONTAINER)

    def close(self):
        self.tap(self.CLOSE_BUTTON)
