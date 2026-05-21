from pages.base_page import BasePage


class IncidentStatusFilter(BasePage):
    """Status filter bottom sheet on the Incidents list.

    Options: In-Triage / Active / Mitigated / Resolved / Closed / Cancelled.
    Locators confirmed by rootly-incident-status_filter.xml.
    """

    HEADER = ("accessibility id", "Status")
    IN_TRIAGE = ("accessibility id", "In-Triage")
    ACTIVE = ("accessibility id", "Active")
    MITIGATED = ("accessibility id", "Mitigated")
    RESOLVED = ("accessibility id", "Resolved")
    CLOSED = ("accessibility id", "Closed")
    CANCELLED = ("accessibility id", "Cancelled")

    OPTIONS = ("In-Triage", "Active", "Mitigated", "Resolved", "Closed", "Cancelled")

    def is_visible(self, timeout=5):
        return super().is_visible(self.HEADER, timeout)

    def select(self, option):
        if option not in self.OPTIONS:
            raise ValueError(f"Status must be one of {self.OPTIONS}, got {option!r}")
        self.tap(("accessibility id", option))

    def dismiss(self):
        self.swipe_down(self.HEADER)
        self.wait_for_gone(self.HEADER, timeout=5)
