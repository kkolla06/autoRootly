from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from pages.base_page import BasePage
from pages.landing_page import LandingPage


class LoginPage(BasePage):
    """Models the embedded web login form opened from the Landing screen.

    Flow: Landing → tap "Log in" → web form (Cancel, email, password, SSO,
    Google link, Slack link, Remember me, Sign in).
    """

    # Email and password fields have empty name/label in the WebView. Match by type.
    EMAIL_FIELD = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeTextField' AND placeholderValue == 'Work email'",
    )
    PASSWORD_FIELD = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeSecureTextField' AND placeholderValue == 'Password'",
    )

    # Show/hide password toggle sits inside the password container at x=306.
    # No name — class chain by sibling position.
    SHOW_PASSWORD_TOGGLE = (
        AppiumBy.IOS_CLASS_CHAIN,
        "**/XCUIElementTypeSecureTextField/following-sibling::XCUIElementTypeButton[1]",
    )

    SIGN_IN_BUTTON = ("accessibility id", "Sign in")
    REMEMBER_ME_SWITCH = ("accessibility id", "Remember me")
    SSO_LINK = ("accessibility id", "SSO")
    CANCEL_BUTTON = ("accessibility id", "Cancel")
    SIGN_IN_HEADER = ("accessibility id", "Sign in")
    OR_DIVIDER = ("accessibility id", "Or")

    # Google and Slack login icons are anonymous links inside the WebView. They sit
    # at x=88 and x=158 respectively, in the order they appear in the DOM. Locate
    # by class chain index until the names are added — see raw_ios_xml/MISSING_XMLS.md.
    GOOGLE_LOGIN_LINK = (
        AppiumBy.IOS_CLASS_CHAIN,
        "**/XCUIElementTypeLink[1]",
    )
    SLACK_LOGIN_LINK = (
        AppiumBy.IOS_CLASS_CHAIN,
        "**/XCUIElementTypeLink[2]",
    )

    # Error surfaces — exact ID not captured in current XML; match generic web errors.
    ERROR_MESSAGE = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeStaticText' AND "
        "(label CONTAINS[c] 'invalid' OR label CONTAINS[c] 'incorrect' OR "
        "label CONTAINS[c] 'wrong' OR label CONTAINS[c] 'required' OR "
        "label CONTAINS[c] 'error')",
    )

    def open_from_landing(self):
        """Tap the Landing screen's Log in button to open the web form."""
        LandingPage(self.driver).tap_log_in()
        self.wait_for_visible(self.EMAIL_FIELD, timeout=15)

    def login(self, email: str, password: str):
        """Full happy-path login: Landing → Log in → fill form → Sign in."""
        if not self.is_visible(self.EMAIL_FIELD, timeout=2):
            self.open_from_landing()
        self.tap(self.EMAIL_FIELD)
        self.type_text(self.EMAIL_FIELD, email)
        self.type_text(self.PASSWORD_FIELD, password)
        self.tap(self.SIGN_IN_BUTTON)
        # Dismiss iOS toast/confirmation that appears after tapping Sign in.
        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(270, 500)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.05)
        actions.pointer_action.release()
        actions.perform()

    def is_form_visible(self, timeout: int = 5) -> bool:
        return (
            self.is_visible(self.EMAIL_FIELD, timeout)
            and self.is_visible(self.PASSWORD_FIELD, timeout=2)
        )

    def cancel(self):
        self.tap(self.CANCEL_BUTTON)

    def toggle_remember_me(self):
        self.tap(self.REMEMBER_ME_SWITCH)

    def remember_me_state(self) -> str:
        """Returns '0' (off) or '1' (on)."""
        return self.find(self.REMEMBER_ME_SWITCH).get_attribute("value")

    def toggle_show_password(self):
        self.tap(self.SHOW_PASSWORD_TOGGLE)

    def password_is_masked(self) -> bool:
        """True when the password input is still a SecureTextField."""
        return self.is_visible(self.PASSWORD_FIELD, timeout=2)

    def tap_sso(self):
        self.tap(self.SSO_LINK)

    def tap_google(self):
        self.tap(self.GOOGLE_LOGIN_LINK)

    def tap_slack(self):
        self.tap(self.SLACK_LOGIN_LINK)

    def get_error_message(self) -> str:
        return self.find(self.ERROR_MESSAGE).text
