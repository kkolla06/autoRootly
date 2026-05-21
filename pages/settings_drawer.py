from pages.base_page import BasePage


class SettingsDrawer(BasePage):
    """Right-edge slide-out drawer seen overlapping the Shifts screen.

    Distinct from the full Settings page (`SettingsPage`). The recording
    showed it appearing as a partial overlay with shortcut rows visible on
    the right edge. Element set is not yet known.

    TODO: locators need raw_ios_xml/MISSING_XMLS.md (#21).
    """

    # Best guess — a row that's likely in the drawer based on the recording.
    # Will be replaced by actual accessibility ids once XML lands.
    DRAWER_ROOT = ("accessibility id", "settings_drawer")
    BACK_HANDLE = ("accessibility id", "settings_drawer_back")

    def is_visible(self, timeout=5):
        return super().is_visible(self.DRAWER_ROOT, timeout)

    def dismiss(self):
        self.tap(self.BACK_HANDLE)
