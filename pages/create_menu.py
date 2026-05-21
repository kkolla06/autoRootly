from pages.base_page import BasePage


class CreateMenu(BasePage):
    """The bottom sheet opened by tapping the '+' / Menu toggle on the bottom nav.

    Contains three creation entry points: Create Incident / Create Alert /
    Create Override. Confirmed from rootly-home-with-create.xml.
    The toggle is still visible when the sheet is open; re-tapping it closes.
    """

    CREATE_INCIDENT = ("accessibility id", "Create Incident")
    CREATE_ALERT = ("accessibility id", "Create Alert")
    CREATE_OVERRIDE = ("accessibility id", "Create Override")
    CLOSE_BUTTON = ("accessibility id", "nav_menu_toggle")

    def is_visible(self, locator=None, timeout=5):
        return super().is_visible(locator if locator is not None else self.CREATE_INCIDENT, timeout)

    def tap_create_incident(self):
        self.tap(self.CREATE_INCIDENT)

    def tap_create_alert(self):
        self.tap(self.CREATE_ALERT)

    def tap_create_override(self):
        self.tap(self.CREATE_OVERRIDE)

    def close(self):
        self.tap(self.CLOSE_BUTTON)
