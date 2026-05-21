from pages.base_page import BasePage


class TypesPicker(BasePage):
    """The Types picker on Create Incident.

    Options vary by org. Mostly free-form list with a Done button.
    TODO: locators need raw_ios_xml/MISSING_XMLS.md (#3).
    """

    HEADER = ("accessibility id", "Types")
    DONE_BUTTON = ("accessibility id", "Done")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def select(self, label):
        self.tap(("accessibility id", label))

    def done(self):
        self.tap(self.DONE_BUTTON)
