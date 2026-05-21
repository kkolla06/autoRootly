from pages.base_page import BasePage


class SelectSchedules(BasePage):
    """The 'Select Schedules' filter sheet on the Shifts screen.

    Opened by tapping the '0 Schedules' chip. Shows a search field, a list
    of schedules (empty in the demo account → 'No schedules to show'), and
    a close X.

    TODO: locators need raw_ios_xml/MISSING_XMLS.md (#19).
    """

    HEADER = ("accessibility id", "Select Schedules")
    SEARCH_FIELD = ("accessibility id", "Search for a schedule")
    CLOSE_BUTTON = ("accessibility id", "Close")
    EMPTY_STATE = ("accessibility id", "No schedules to show")

    def is_visible(self, locator=None, timeout=5):
        return super().is_visible(locator if locator is not None else self.HEADER, timeout)

    def is_empty_state_visible(self, timeout=5):
        return self.is_visible(self.EMPTY_STATE, timeout)

    def search(self, text):
        self.type_text(self.SEARCH_FIELD, text)

    def close(self):
        self.tap(self.CLOSE_BUTTON)
