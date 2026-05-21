from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class CreateIncidentPage(BasePage):
    """The Create Incident form (opened from + tab → Create Incident).

    Fields confirmed in rootly-incident_create.xml: Title, Summary, Severity
    (StaticText label — not required), Types dropdown, Mark as Private toggle.
    Submit fires the toast 'Incident created successfully'.
    """

    HEADER = ("accessibility id", "Create Incident")
    CLOSE_BUTTON = ("accessibility id", "Close")

    TITLE_FIELD = ("accessibility id", "Add a brief incident title")

    # The visible label above the field is "Summary"; the placeholder
    # accessibility id remains 'Describe the impact of the incident'.
    SUMMARY_FIELD = ("accessibility id", "Describe the impact of the incident")
    # Backwards-compat alias for tests that still call .fill_description().
    DESCRIPTION_FIELD = SUMMARY_FIELD

    SEVERITY_LABEL = ("accessibility id", "Severity")
    TYPES_BUTTON = ("accessibility id", "Types")
    PRIVATE_SWITCH = ("accessibility id", "Mark as Private")

    SUBMIT_BUTTON = ("accessibility id", "Create Incident")
    SUBMIT_CONTAINER = ("accessibility id", "create_incident_page_create_button")

    # Inline error appearing under Title when submit is attempted empty.
    TITLE_ERROR = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND "
        "(label CONTAINS[c] 'title' AND label CONTAINS[c] 'required')",
    )

    def is_visible(self, locator=None, timeout=5):
        return super().is_visible(locator if locator is not None else self.SUBMIT_BUTTON, timeout)

    def fill_title(self, title):
        self.type_text(self.TITLE_FIELD, title)

    def fill_summary(self, summary):
        self.type_text(self.SUMMARY_FIELD, summary)

    # Backwards-compat alias.
    fill_description = fill_summary

    def open_types(self):
        self.tap(self.TYPES_BUTTON)

    def toggle_private(self):
        self.tap(self.PRIVATE_SWITCH)

    def private_state(self):
        """'0' off, '1' on."""
        return self.find(self.PRIVATE_SWITCH).get_attribute("value")

    def submit(self):
        self.tap(self.SUBMIT_BUTTON)

    def close(self):
        self.tap(self.CLOSE_BUTTON)

    def fill_and_submit(self, title, description=""):
        self.fill_title(title)
        if description:
            self.fill_summary(description)
        self.submit()

    def title_error_visible(self, timeout=3):
        return self.is_visible(self.TITLE_ERROR, timeout)
