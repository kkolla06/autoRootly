import os
import re
from html import escape
import pytest
from pytest_html import extras


_report_data: list = []

_FEATURE_MARKERS = frozenset({
    "landing", "login", "home", "incident", "alerts",
    "shifts", "settings", "navigation", "e2e", "edge",
})

_TC_RE = re.compile(r"(TC-[A-Z0-9]+(?:-[A-Za-z0-9]+)+)\s*[—–\-]\s*(.*)")


def _parse_docstring(doc: str):
    """Return (tc_id, description) from the first line of a test docstring."""
    first = (doc or "").strip().split("\n")[0].strip()
    m = _TC_RE.match(first)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return "", first[:100] if first else ""


@pytest.fixture(autouse=True)
def screenshot_on_failure(driver, request, extra):
    """Save a screenshot on failure and embed it in the HTML report."""
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        os.makedirs("assets", exist_ok=True)
        name = request.node.name.replace(" ", "_")
        path = f"assets/FAILED_{name}.png"
        driver.save_screenshot(path)
        extra.append(extras.image(path))


@pytest.fixture(autouse=True)
def add_test_metadata(request, extra):
    """Inject TC-ID, feature/priority badges, and description into the row details."""
    doc = getattr(request.node.function, "__doc__", "") or ""
    tc_id, description = _parse_docstring(doc)
    kw = set(request.node.keywords.keys())
    feature = next((m for m in _FEATURE_MARKERS if m in kw), "")
    priority = next((p for p in ("p0", "p1", "p2", "p3") if p in kw), "")

    parts = []
    if tc_id:
        parts.append(f'<span class="rly-tc-id">{escape(tc_id)}</span>')
    if feature:
        parts.append(
            f'<span class="rly-badge rly-feature-{escape(feature)}">'
            f'{escape(feature)}</span>'
        )
    if priority:
        parts.append(
            f'<span class="rly-badge rly-{escape(priority)}">'
            f'{escape(priority)}</span>'
        )
    if description:
        parts.append(f'<span class="rly-desc-text">{escape(description)}</span>')

    if parts:
        extra.append(extras.html(
            f'<div class="rly-test-meta">{"&nbsp;".join(parts)}</div>'
        ))
    yield


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    if rep.when == "call":
        doc = getattr(item.function, "__doc__", None) or ""
        tc_id, description = _parse_docstring(doc)
        kw = set(item.keywords.keys())
        feature = next((m for m in _FEATURE_MARKERS if m in kw), "")
        priority = next((p for p in ("p0", "p1", "p2", "p3") if p in kw), "")

        rep._rly_tc_id = tc_id
        rep._rly_description = description
        rep._rly_feature = feature
        rep._rly_priority = priority

        _report_data.append({
            "outcome": rep.outcome,
            "feature": feature,
            "priority": priority,
        })
