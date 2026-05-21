from pages.base_page import BasePage


class AlertAddNoteSheet(BasePage):
    """'Add note' bottom sheet opened from the + action menu.

    Confirmed from rootly-alert_addnote.xml.

    Single multi-line TextField + 'Add note' submit button.
    No close button — dismiss via BasePage.dismiss_sheet() (swipe down).
    No toast after successful submission — the sheet simply closes.
    Button is enabled even when the field is empty; the app rejects empty
    submits by keeping the sheet open (verified at runtime).
    """

    NOTE_FIELD = ("accessibility id", "Anything you want to add to the alert?")
    SUBMIT_CONTAINER = ("accessibility id", "note_bottom_sheet_add_note_button")
    SUBMIT_BUTTON = ("accessibility id", "Add note")

    def is_visible(self, timeout=5):
        return super().is_visible(self.NOTE_FIELD, timeout)

    def fill_note(self, text):
        self.type_text(self.NOTE_FIELD, text)

    def submit(self):
        self.tap(self.SUBMIT_CONTAINER)

    def close(self):
        self.dismiss_sheet()
