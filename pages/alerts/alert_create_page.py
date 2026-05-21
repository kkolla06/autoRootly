from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from pages.base_page import BasePage


class AlertCreatePage(BasePage):
    """The Create Alert form (opened from + tab → Create Alert).

    Required: Who do you want to notify? (Select Responders sheet) + Urgency
    + Title. Optional: Description. Submitting fires a manual page and shows
    the toast 'Manual page created successfully'.
    """

    # Confirmed in rootly-alert_create.xml
    HEADER = ("accessibility id", "Create Alert")
    CLOSE_BUTTON = ("accessibility id", "Close")
    TITLE_FIELD = ("accessibility id", "Title *")
    DESCRIPTION_FIELD = ("accessibility id", "Description")

    # StaticText confirmed in normal-state XML (name="Who do you want to notify? *").
    # open_responder_picker() uses a coordinate tap because element.click() on a
    # StaticText inside a visible=false ancestor does not fire the sheet.
    NOTIFY_DROPDOWN = (
        AppiumBy.IOS_PREDICATE,
        "name == 'Who do you want to notify? *'",
    )
    URGENCY_DROPDOWN = (
        AppiumBy.IOS_PREDICATE,
        "label CONTAINS 'Urgency'",
    )

    # Two locators for the submit button — the recording shows the same control
    # carries both accessibility IDs (a parent container + the button itself).
    SUBMIT_BUTTON = ("accessibility id", "Create Alert and start paging")
    SUBMIT_CONTAINER = ("accessibility id", "manual_page_create_button")

    # Validation errors (inline, appear under the field on empty submit).
    # TITLE_ERROR: a new StaticText that only exists in the DOM when there's an error.
    # NOTIFY_ERROR: the notify-label StaticText changes from visible=false to visible=true
    #   and its label grows to include the error suffix after a newline. Using visible==1
    #   in the predicate so iOS-layer filtering handles the transition reliably.
    TITLE_ERROR = ("accessibility id", "Please enter a title.")
    NOTIFY_ERROR = (
        AppiumBy.IOS_PREDICATE,
        "label CONTAINS[c] 'Please specify who you want to notify'",
    )

    # Responder chip — appears in the Notify section after a responder is
    # picked from the Select Responders sheet. Each chip carries the
    # responder's display name (e.g. 'Kaushik Kolla') as its accessibility id.

    def is_visible(self, timeout=5):
        return super().is_visible(self.SUBMIT_BUTTON, timeout)

    def fill_title(self, title):
        self.type_text(self.TITLE_FIELD, title)

    def fill_description(self, description):
        self.type_text(self.DESCRIPTION_FIELD, description)

    def open_responder_picker(self):
        # NOTIFY_DROPDOWN lives inside a visible=false ancestor so .rect returns
        # wrong coordinates (~5,30). Tap the known on-screen position instead.
        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(180, 220)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.05)
        actions.pointer_action.release()
        actions.perform()

    def open_urgency_picker(self):
        self.tap(self.URGENCY_DROPDOWN)

    def get_urgency(self):
        """Returns the currently-displayed urgency value (e.g. 'High')."""
        return self.find(self.URGENCY_DROPDOWN).get_attribute("value")

    def submit(self):
        self.tap(self.SUBMIT_BUTTON)

    def close(self):
        self.tap(self.CLOSE_BUTTON)

    def fill_and_submit(self, title, description=""):
        self.fill_title(title)
        if description:
            self.fill_description(description)
        self.submit()

    def title_error_visible(self, timeout=3):
        return super().is_visible(self.TITLE_ERROR, timeout)

    def notify_error_visible(self, timeout=3):
        try:
            self.find(self.NOTIFY_ERROR, timeout)
            return True
        except Exception:
            return False

    def responder_chip_visible(self, name, timeout=5):
        """True when a responder chip for `name` is rendered in the form."""
        locator = (
            AppiumBy.IOS_PREDICATE,
            f"name == '{name}' OR label == '{name}'",
        )
        return super().is_visible(locator, timeout)
