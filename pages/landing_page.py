from pages.base_page import BasePage


class LandingPage(BasePage):
    # Confirmed from rootly-landing.xml and rootly-login_confirm.xml
    LOG_IN_BUTTON = ("accessibility id", "Log in")
    TAGLINE = (
        "accessibility id",
        "See your shifts, create overrides, manage alerts, and never miss a page.",
    )

    def is_visible(self, locator=None, timeout: int = 10) -> bool:
        return super().is_visible(locator if locator is not None else self.LOG_IN_BUTTON, timeout)

    def tap_log_in(self):
        self.tap(self.LOG_IN_BUTTON)
        # Dismiss the "Rootly wants to sign in" ASWebAuthenticationSession alert
        try:
            self.driver.execute_script("mobile: alert", {"action": "accept"})
        except Exception:
            pass
