from pathlib import Path

import pytest
from playwright.sync_api import Page, expect


SCREENSHOTDIR = Path(__file__).resolve().parents[1] / "reports" / "screenshots"


@pytest.fixture
def screenshotpage(page: Page):
    SCREENSHOTDIR.mkdir(parents=True, exist_ok=True)

    page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Screenshot Practice</title>
            <style>
                body {
                    font-family: Arial;
                    margin: 30px;
                }

                #loginform {
                    border: 1px solid gray;
                    padding: 20px;
                    width: 300px;
                }

                input, button {
                    display: block;
                    margin: 10px 0;
                    padding: 8px;
                }

                .section {
                    height: 250px;
                    padding: 15px;
                    border: 1px solid lightgray;
                }

                #error {
                    color: red;
                }
            </style>
        </head>
        <body>
            <h1>Login Application</h1>

            <div id="loginform">
                <label for="username">Username</label>
                <input id="username">

                <label for="password">Password</label>
                <input id="password" type="password">

                <button id="login">Login</button>

                <p id="error" hidden>Invalid credentials</p>
                <h2 id="dashboard" hidden>Dashboard</h2>
            </div>

            <div class="section">Section 1</div>
            <div class="section">Section 2</div>
            <div class="section">Section 3</div>

            <script>
                document.querySelector("#login").addEventListener("click", () => {
                    const username =
                        document.querySelector("#username").value;

                    const password =
                        document.querySelector("#password").value;

                    if (username === "meghana" && password === "test123") {
                        document.querySelector("#dashboard").hidden = false;
                        document.querySelector("#error").hidden = true;
                    } else {
                        document.querySelector("#error").hidden = false;
                        document.querySelector("#dashboard").hidden = true;
                    }
                });
            </script>
        </body>
        </html>
    """)

    yield page


# 1. Capture the current viewport
def testviewportscreenshot(screenshotpage: Page):
    screenshotpath = SCREENSHOTDIR / "viewport.png"

    screenshotpage.screenshot(path=str(screenshotpath))

    assert screenshotpath.exists()
    assert screenshotpath.stat().st_size > 0


# 2. Capture the complete scrollable page
def testfullpagescreenshot(screenshotpage: Page):
    screenshotpath = SCREENSHOTDIR / "fullpage.png"

    screenshotpage.screenshot(
        path=str(screenshotpath),
        full_page=True
    )

    assert screenshotpath.exists()
    assert screenshotpath.stat().st_size > 0


# 3. Capture an individual element
def testelementscreenshot(screenshotpage: Page):
    screenshotpath = SCREENSHOTDIR / "loginform.png"

    screenshotpage.locator("#loginform").screenshot(
        path=str(screenshotpath)
    )

    assert screenshotpath.exists()
    assert screenshotpath.stat().st_size > 0


# 4. Capture a screenshot after displaying an error
def testerrorscreenshot(screenshotpage: Page):
    screenshotpage.locator("#username").fill("wronguser")
    screenshotpage.locator("#password").fill("wrongpassword")
    screenshotpage.locator("#login").click()

    expect(screenshotpage.locator("#error")).to_be_visible()

    screenshotpath = SCREENSHOTDIR / "loginerror.png"
    screenshotpage.screenshot(path=str(screenshotpath))

    assert screenshotpath.exists()


# 5. Demonstrate custom screenshot capture when a test fails
@pytest.fixture
def capturefailure(request, screenshotpage: Page):
    yield screenshotpage

    if hasattr(request.node, "rep_call"):
        if request.node.rep_call.failed:
            SCREENSHOTDIR.mkdir(parents=True, exist_ok=True)

            screenshotpath = SCREENSHOTDIR / (
                f"{request.node.name}.png"
            )

            screenshotpage.screenshot(path=str(screenshotpath))
            print(f"\nFailure screenshot saved: {screenshotpath}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)


# 6. Intentionally failing test to demonstrate failure evidence
@pytest.mark.xfail(
    strict=True,
    reason="Intentional failure to practise screenshot debugging"
)
def testintentionalfailure(capturefailure: Page):
    capturefailure.locator("#username").fill("meghana")

    # This assertion intentionally fails.
    expect(capturefailure.locator("#dashboard")).to_be_visible()