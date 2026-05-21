from pages.base_page import BasePage


class UrgencyPicker(BasePage):
    """The Urgency picker shared by Create Alert + Escalate forms.

    Options likely: Low / Medium / High.
    TODO: locators need raw_ios_xml/MISSING_XMLS.md (#4).
    """

    HEADER = ("accessibility id", "Urgency")
    OPTIONS = ("Low", "Medium", "High")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def select(self, level):
        if level not in self.OPTIONS:
            raise ValueError(f"Urgency must be one of {self.OPTIONS}, got {level!r}")
        self.tap(("accessibility id", level))
