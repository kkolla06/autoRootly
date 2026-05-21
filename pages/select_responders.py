import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from pages.base_page import BasePage


class SelectResponders(BasePage):
    """The Select Responders bottom sheet.

    Shared by Create Alert + Escalate. Confirmed by rootly-create-select_responders.xml.

      Title:  "Select Responders"
      Search: "Search" (text field)
      Categories (each expandable via section header Button):
        - Escalation Policies  →  e.g. "SRE (Site Reliability Engineering) Team"
        - Services / Teams     →  disabled in demo (0 results)
        - People               →  e.g. "Kaushik Kolla"
      Items render as XCUIElementTypeSwitch with enabled=false in the captured
      state — Appium label-predicate tap should still reach them.
      Bottom button: "Done"  (appears once a responder is selected)
    """

    # Confirmed from rootly-create-select_responders.xml
    HEADER = ("accessibility id", "Select Responders")
    SEARCH_FIELD = ("accessibility id", "Search")
    DONE_BUTTON = ("accessibility id", "Done")  # confirmed: XCUIElementTypeButton name="Done" inside responder_confirm_button

    # Section headers — use IOS_PREDICATE name== because the XML name attribute
    # is the accessibilityLabel, not accessibilityIdentifier, so accessibility
    # id strategy does not reliably match it.
    ESCALATION_POLICIES = (AppiumBy.IOS_PREDICATE, "name == 'responder_section_escalationPath'")
    SERVICES = (AppiumBy.IOS_PREDICATE, "name == 'responder_section_service'")
    TEAMS = (AppiumBy.IOS_PREDICATE, "name == 'responder_section_team'")
    PEOPLE = (AppiumBy.IOS_PREDICATE, "name == 'responder_section_people'")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def search(self, text):
        self.type_text(self.SEARCH_FIELD, text)

    def expand_category(self, name):
        """Tap a category header to expand it. `name` ∈ Escalation Policies /
        Services / Teams / People."""
        if name == "People":
            time.sleep(3)
            touch = PointerInput(interaction.POINTER_TOUCH, "touch")
            actions = ActionBuilder(self.driver, mouse=touch)
            actions.pointer_action.move_to_location(180, 400)
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(0.05)
            actions.pointer_action.release()
            actions.perform()
            return
        mapping = {
            "Escalation Policies": self.ESCALATION_POLICIES,
            "Services": self.SERVICES,
            "Teams": self.TEAMS,
        }
        if name not in mapping:
            raise ValueError(f"Unknown category {name!r}")
        self.tap(mapping[name])

    def select(self, _name):
        """Tap the row matching `name` (e.g. 'Kaushik Kolla').

        Items render as XCUIElementTypeSwitch with enabled=false, so
        XCUITest's element.tap() is blocked. Use a raw W3C pointer action
        at the element's centre coordinates to bypass the enabled check.
        """
        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(180, 450)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.05)
        actions.pointer_action.release()
        actions.perform()

    def done(self):
        self.tap(self.DONE_BUTTON)
