from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from appium.webdriver.common.appiumby import AppiumBy


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def find(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def find_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def tap(self, locator, timeout=10):
        for attempt in range(3):
            try:
                self.find(locator, timeout).click()
                return
            except StaleElementReferenceException:
                if attempt == 2:
                    raise

    def type_text(self, locator, text, timeout=10):
        el = self.find(locator, timeout)
        el.clear()
        el.send_keys(text)

    def wait_for_visible(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_gone(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )

    def is_visible(self, locator, timeout=5):
        try:
            self.find_visible(locator, timeout)
            return True
        except Exception:
            return False

    def take_screenshot(self, name):
        self.driver.save_screenshot(f"assets/{name}.png")

    def scroll_down(self):
        size = self.driver.get_window_size()
        self.driver.swipe(
            start_x=size["width"] // 2,
            start_y=int(size["height"] * 0.8),
            end_x=size["width"] // 2,
            end_y=int(size["height"] * 0.2),
            duration=500,
        )

    def swipe_down(self, locator, distance=400, duration_ms=400, timeout=10):
        """Drag downward from the top-centre of `locator` by `distance` pixels.

        Used to dismiss bottom sheets that have no close button — dragging the
        sheet header far enough down flings it off-screen on iOS.
        """
        el = self.find(locator, timeout)
        rect = el.rect
        x = rect["x"] + rect["width"] // 2
        start_y = rect["y"] + 4
        end_y = start_y + distance

        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(x, start_y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(duration_ms / 1000)
        actions.pointer_action.move_to_location(x, end_y)
        actions.pointer_action.release()
        actions.perform()

    def dismiss_sheet(self):
        """Screen-level downward swipe to dismiss an open bottom sheet.

        Use when no sheet page-object or header locator is available.
        Equivalent to the user swiping down from the middle of the screen.
        """
        self.driver.execute_script("mobile: swipe", {"direction": "down"})

    def slide(self, locator, direction="right", duration_ms=600, padding=12, timeout=10):
        """Perform a slide gesture across the width of `locator`.

        Used for the alert detail "Slide to ack" / "Slide to resolve" controls,
        which look like a track with a handle that must be dragged to the
        opposite end. `direction` is "right" (default) or "left". `padding`
        keeps the start/end points just inside the bounds so iOS treats the
        gesture as a drag on the element, not a tap on the surrounding view.
        """
        el = self.find(locator, timeout)
        rect = el.rect  # {'x','y','width','height'}
        y = rect["y"] + rect["height"] // 2
        left_x = rect["x"] + padding
        right_x = rect["x"] + rect["width"] - padding

        if direction == "right":
            start_x, end_x = left_x, right_x
        elif direction == "left":
            start_x, end_x = right_x, left_x
        else:
            raise ValueError(f"slide direction must be 'right' or 'left', got {direction!r}")

        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(start_x, y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(duration_ms / 1000)
        actions.pointer_action.move_to_location(end_x, y)
        actions.pointer_action.release()
        actions.perform()

    def wait_for_toast(self, text, timeout=10):
        """Wait for a toast containing `text` to appear. Returns the element.

        Rootly's success toasts (`Incident created successfully`,
        `Manual page created successfully`, `You have escalated successfully`)
        are short-lived StaticText elements that float above the bottom nav.
        """
        locator = (
            AppiumBy.IOS_PREDICATE,
            f"type == 'XCUIElementTypeStaticText' AND label CONTAINS[c] '{text}'",
        )
        return self.wait_for_visible(locator, timeout)

    def tap_coordinate(self, x, y):
        """Tap an exact screen coordinate using W3C pointer actions.

        Use only when no name/label is available and a coordinate tap is the
        only reliable way to hit the element (e.g. the nameless more-menu icon
        on the incident detail screen).
        """
        touch = PointerInput(interaction.POINTER_TOUCH, "touch")
        actions = ActionBuilder(self.driver, mouse=touch)
        actions.pointer_action.move_to_location(x, y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.1)
        actions.pointer_action.release()
        actions.perform()

    def wait_for_toast_gone(self, text, timeout=15):
        """Wait for a toast containing `text` to disappear."""
        locator = (
            AppiumBy.IOS_PREDICATE,
            f"type == 'XCUIElementTypeStaticText' AND label CONTAINS[c] '{text}'",
        )
        return self.wait_for_gone(locator, timeout)

    def by_accessibility_id(self, value):
        return (AppiumBy.ACCESSIBILITY_ID, value)

    def by_class(self, value):
        return (AppiumBy.CLASS_NAME, value)

    def by_predicate(self, value):
        return (AppiumBy.IOS_PREDICATE, value)

    def by_class_chain(self, value):
        return (AppiumBy.IOS_CLASS_CHAIN, value)
