from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class ShiftsPage(BasePage):
    # Confirmed from rootly-shifts.xml — header is an image with name "Shifts\nMay "
    SHIFTS_HEADER = (
        AppiumBy.IOS_PREDICATE,
        "name BEGINSWITH 'Shifts' AND type == 'XCUIElementTypeImage'",
    )
    MY_SHIFTS_TAB = ("accessibility id", "My shifts")
    ALL_SHIFTS_TAB = ("accessibility id", "All shifts")
    # "0 Schedules" — count varies, use BEGINSWITH digit
    SCHEDULES_COUNT = (
        AppiumBy.IOS_PREDICATE,
        "label ENDSWITH 'Schedules' OR label ENDSWITH 'Schedule'",
    )
    EMPTY_STATE = (
        "accessibility id",
        "No shifts available. Please adjust your schedule filters to view upcoming shifts.",
    )
    SETTINGS_AVATAR = ("accessibility id", "KK")

    def is_visible(self, timeout: int = 5) -> bool:
        return super().is_visible(self.SHIFTS_HEADER, timeout)

    def tap_my_shifts(self):
        self.tap(self.MY_SHIFTS_TAB)

    def tap_all_shifts(self):
        self.tap(self.ALL_SHIFTS_TAB)

    def is_empty_state_visible(self) -> bool:
        return self.is_visible(self.EMPTY_STATE, timeout=5)

    def open_settings(self):
        self.tap(self.SETTINGS_AVATAR)
