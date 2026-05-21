---
name: feedback-xml-capture
description: How XML captures are obtained and what the current set represents
metadata:
  type: feedback
---

User drives Appium Inspector to capture XMLs; agent maintains MISSING_XMLS.md and uses captured XMLs for locators.

**The XMLs in raw_ios_xml/ are the COMPLETE set — nothing is collapsed or unexpanded.** Do not assume additional elements exist beyond what is shown. If a locator isn't derivable from the existing XMLs, add it to MISSING_XMLS.md and ask the user to capture.

**Why:** User confirmed 2026-05-20 that all provided XMLs are fully expanded with no hidden content.

**How to apply:** Never write speculative locators based on guessing element structure. Only use locators confirmed from actual XML captures.
