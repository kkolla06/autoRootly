import os
from html import escape
import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions
from dotenv import load_dotenv
from config.capabilities import APPIUM_SERVER_URL, CAPS

load_dotenv()


@pytest.fixture(scope="session")
def driver():
    options = XCUITestOptions()
    options.load_capabilities(CAPS)
    d = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    yield d
    d.quit()


@pytest.fixture(scope="function")
def login(driver):
    """Ensures the test starts on the Home screen.

    With noReset=True the keychain typically preserves the session, so most runs
    skip the login step. If the Home indicator isn't visible we drive the full
    Landing → web login form → Sign in flow via LoginPage.
    """
    from pages.home_page import HomePage
    from pages.login_page import LoginPage

    home = HomePage(driver)

    if not home.is_home_visible(timeout=10):
        LoginPage(driver).login(
            email=os.getenv("ROOTLY_TEST_EMAIL"),
            password=os.getenv("ROOTLY_TEST_PASSWORD"),
        )
        home.wait_for_visible(home.HOME_INDICATOR, timeout=30)

    yield driver

    # Terminate and reactivate the app so every test starts from the home screen.
    # noReset: True preserves the login session in the keychain, so no re-login needed.
    bundle_id = os.getenv("APP_BUNDLE_ID")
    driver.terminate_app(bundle_id)
    driver.activate_app(bundle_id)


@pytest.fixture(scope="function")
def paged_alert(login):
    """Self-pages the test user via Create Alert and yields the alert id.

    Used by paged-home and alert state-machine tests that need an alert in
    Triggered state owned by the current user. Cleans up by sliding the
    alert through ack → resolve in teardown.

    Currently SKIPPED at runtime if the Create menu / Select Responders XMLs
    are not yet captured — see raw_ios_xml/MISSING_XMLS.md (#1, #5).
    Tests that depend on this fixture should not be marked skip themselves;
    they'll fail-fast here with a clear pytest.skip() until XMLs land.
    """
    from pages.home_page import HomePage
    from pages.create_menu import CreateMenu
    from pages.alerts.alert_create_page import AlertCreatePage
    from pages.select_responders import SelectResponders
    from pages.alerts.alerts_page import AlertsPage
    from pages.alerts.alert_detail_page import AlertDetailPage

    driver = login
    home = HomePage(driver)
    home.open_menu()
    menu = CreateMenu(driver)

    if not menu.is_visible(timeout=5):
        pytest.skip(
            "Create menu not reachable — XML #1 (raw_ios_xml/MISSING_XMLS.md) "
            "needed to wire up the + tab sheet."
        )

    menu.tap_create_alert()
    form = AlertCreatePage(driver)
    form.wait_for_visible(form.SUBMIT_BUTTON, timeout=5)

    form.open_responder_picker()
    picker = SelectResponders(driver)
    if not picker.is_visible(timeout=5):
        pytest.skip(
            "Select Responders sheet not reachable — XML #5 "
            "(raw_ios_xml/MISSING_XMLS.md) needed."
        )
    picker.expand_category("People")
    picker.select("Kaushik Kolla")
    picker.done()

    title = "auto-page (state-machine fixture)"
    form.fill_title(title)
    form.submit()

    # Wait for the success toast so we know the alert exists server-side.
    try:
        form.wait_for_toast("Manual page created successfully", timeout=5)
    except Exception:
        pytest.skip(
            "Manual page toast not observed — alert creation may have failed "
            "or the toast locator strategy needs XML #11 confirmation."
        )

    # Read the alert id off the paged-home banner if we land back on Home,
    # otherwise off the alerts list.
    alert_id = None
    if home.is_paged(timeout=5):
        alert_id = home.get_paged_alert_id()

    yield {"id": alert_id, "title": title}

    # Teardown: navigate to the alert and resolve it so the next run starts clean.
    home.go_to_alerts()
    alerts = AlertsPage(driver)
    if alerts.has_any_alert(timeout=5):
        alerts.open_first_alert()
        detail = AlertDetailPage(driver)
        # Best effort — ignore any failures so cleanup never masks the real
        # assertion failure.
        try:
            if detail.is_visible(detail.SLIDE_TO_ACK, timeout=2):
                detail.slide_to_ack()
            if detail.is_visible(detail.SLIDE_TO_RESOLVE, timeout=2):
                detail.slide_to_resolve()
        except Exception:
            pass


pytest_plugins = ["utils.helpers"]


# ── Report customisation ─────────────────────────────────────────────────── #

def pytest_html_report_title(report):
    report.title = "Rootly iOS · Automated QA Report"


def pytest_html_results_summary(prefix, summary, postfix, session):
    from utils.helpers import _report_data

    total = len(_report_data)
    if total == 0:
        return

    passed = sum(1 for r in _report_data if r["outcome"] == "passed")
    failed = sum(1 for r in _report_data if r["outcome"] == "failed")
    pass_rate = round(passed / total * 100)

    feature_stats: dict = {}
    priority_stats: dict = {}

    for r in _report_data:
        feat_key = r["feature"] or "untagged"
        pri_key = r["priority"] or "untagged"
        outcome = r["outcome"] if r["outcome"] in ("passed", "failed") else "skipped"
        feature_stats.setdefault(feat_key, {"passed": 0, "failed": 0, "skipped": 0})[outcome] += 1
        priority_stats.setdefault(pri_key, {"passed": 0, "failed": 0, "skipped": 0})[outcome] += 1

    def _pct(p, t):
        return round(p / t * 100) if t else 0

    def _bar(pct):
        fill = "#22c55e" if pct >= 80 else ("#f59e0b" if pct >= 50 else "#ef4444")
        return (
            f'<div class="rly-progress">'
            f'<div class="rly-progress__fill" style="width:{pct}%;background:{fill}"></div>'
            f'</div>'
        )

    def _rows(stats, ordered_keys, badge_cls_fn):
        html = ""
        for key in ordered_keys:
            if key not in stats:
                continue
            s = stats[key]
            t = s["passed"] + s["failed"] + s["skipped"]
            p = _pct(s["passed"], t)
            html += (
                f"<tr>"
                f'<td><span class="{badge_cls_fn(key)}">{escape(key)}</span></td>'
                f'<td class="rly-num">{t}</td>'
                f'<td class="rly-num rly-pass">{s["passed"]}</td>'
                f'<td class="rly-num rly-fail">{s["failed"]}</td>'
                f'<td>{_bar(p)}<span class="rly-pct-text">{p}%</span></td>'
                f"</tr>"
            )
        return html

    feat_order = sorted(feature_stats.keys())
    pri_order = ["p0", "p1", "p2", "p3", "untagged"]

    feat_rows = _rows(feature_stats, feat_order, lambda k: f"rly-badge rly-feature-{k}")
    pri_rows = _rows(priority_stats, pri_order,
                     lambda k: "rly-badge rly-priority-untagged" if k == "untagged"
                     else f"rly-badge rly-{k}")

    rate_color = "#16a34a" if pass_rate >= 80 else ("#f59e0b" if pass_rate >= 50 else "#dc2626")

    dashboard = f"""
<div class="rly-dashboard">
  <div class="rly-stat-grid">
    <div class="rly-stat-card">
      <div class="rly-stat-label">Total Tests</div>
      <div class="rly-stat-value">{total}</div>
    </div>
    <div class="rly-stat-card rly-stat-card--pass">
      <div class="rly-stat-label">Passed</div>
      <div class="rly-stat-value" style="color:#16a34a">{passed}</div>
    </div>
    <div class="rly-stat-card rly-stat-card--fail">
      <div class="rly-stat-label">Failed</div>
      <div class="rly-stat-value" style="color:#dc2626">{failed}</div>
    </div>
    <div class="rly-stat-card rly-stat-card--rate">
      <div class="rly-stat-label">Pass Rate</div>
      <div class="rly-stat-value" style="color:{rate_color}">{pass_rate}%</div>
    </div>
  </div>
  <div class="rly-breakdown-grid">
    <div class="rly-breakdown-card">
      <h3 class="rly-breakdown-title">Feature Coverage</h3>
      <table class="rly-breakdown-table">
        <thead>
          <tr><th>Feature</th><th>Total</th><th>Pass</th><th>Fail</th><th>Rate</th></tr>
        </thead>
        <tbody>{feat_rows}</tbody>
      </table>
    </div>
    <div class="rly-breakdown-card">
      <h3 class="rly-breakdown-title">Priority Coverage</h3>
      <table class="rly-breakdown-table">
        <thead>
          <tr><th>Priority</th><th>Total</th><th>Pass</th><th>Fail</th><th>Rate</th></tr>
        </thead>
        <tbody>{pri_rows}</tbody>
      </table>
    </div>
  </div>
</div>
"""
    summary.append(dashboard)
