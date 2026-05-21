from pages.base_page import BasePage


class SeverityPicker(BasePage):
    """The Severity picker on Create Incident.

    Options likely include SEV0..SEV5 (matches incident list badges).
    TODO: locators need raw_ios_xml/MISSING_XMLS.md (#2).
    """

    HEADER = ("accessibility id", "Severity")
    OPTIONS = ("SEV0", "SEV1", "SEV2", "SEV3", "SEV4", "SEV5")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def select(self, level):
        if level not in self.OPTIONS:
            raise ValueError(f"Severity must be one of {self.OPTIONS}, got {level!r}")
        self.tap(("accessibility id", level))
