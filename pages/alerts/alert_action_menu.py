from pages.base_page import BasePage


class AlertActionMenu(BasePage):
    """The '+' action menu on alert detail.

    State-dependent options confirmed by rootly-alert_action_menu_*.xml:
      Triggered    → Resolve, Escalate, Add note, Mark as noise, Create Incident, Share
      Acknowledged → Escalate, Add note, Mark as noise, Create Incident, Share
      Resolved     → Add note, Mark as noise, Create Incident, Share

    Note: CLOSE_BUTTON ("Close") not observed in any captured XML; may not exist.
    """

    RESOLVE = ("accessibility id", "Resolve")
    ESCALATE = ("accessibility id", "Escalate")
    ADD_NOTE = ("accessibility id", "Add note")
    MARK_AS_NOISE = ("accessibility id", "Mark as noise")
    CREATE_INCIDENT = ("accessibility id", "Create Incident")
    SHARE = ("accessibility id", "Share")
    CLOSE_BUTTON = ("accessibility id", "Close")

    ALWAYS_PRESENT = ("Add note", "Mark as noise", "Create Incident", "Share")

    def is_visible(self, timeout=5):
        return super().is_visible(self.ADD_NOTE, timeout)

    def is_escalate_visible(self, timeout=3):
        return super().is_visible(self.ESCALATE, timeout)

    def is_visible_option(self, name, timeout=2):
        """Check a single named option is visible. Avoids comprehension super() issues."""
        mapping = {
            "Resolve": self.RESOLVE,
            "Escalate": self.ESCALATE,
            "Add note": self.ADD_NOTE,
            "Mark as noise": self.MARK_AS_NOISE,
            "Create Incident": self.CREATE_INCIDENT,
            "Share": self.SHARE,
        }
        return super().is_visible(mapping[name], timeout)

    def tap_resolve(self):
        self.tap(self.RESOLVE)

    def tap_escalate(self):
        self.tap(self.ESCALATE)

    def tap_add_note(self):
        self.tap(self.ADD_NOTE)

    def tap_mark_as_noise(self):
        self.tap(self.MARK_AS_NOISE)

    def tap_create_incident(self):
        self.tap(self.CREATE_INCIDENT)

    def tap_share(self):
        self.tap(self.SHARE)

    def close(self):
        self.tap(self.CLOSE_BUTTON)

    def visible_options(self):
        """Returns the subset of {Escalate, Add note, ...} actually visible."""
        candidates = {
            "Resolve": self.RESOLVE,
            "Escalate": self.ESCALATE,
            "Add note": self.ADD_NOTE,
            "Mark as noise": self.MARK_AS_NOISE,
            "Create Incident": self.CREATE_INCIDENT,
            "Share": self.SHARE,
        }
        result = set()
        for name, loc in candidates.items():
            if super().is_visible(loc, timeout=2):
                result.add(name)
        return result
