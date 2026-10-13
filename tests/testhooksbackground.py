from pathlib import Path

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import Page, expect


# Load all scenarios from the feature file
scenarios("login.feature")


# Hook-style setup and teardown using pytest fixtures
@pytest.fixture
def loginpage(page: Page):
    print("\nBefore hook: Preparing login test")
    yield page
    print("\nAfter hook: Login test cleanup")


# Common Background step
@given("the login page is open")
def openloginpage(loginpage: Page):
    loginpage.set_content("""
        <h1>Login</h1>

        <label for="username">Username</label>
        <input id="username">

        <label for="password">Password</label>
        <input id="password" type="password">

        <button id="login">Login</button>

        <h2 id="dashboard" hidden>Dashboard</h2>
        <p id="error" hidden>Invalid username or password</p>

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
    """)


# Scenario action: valid credentials
@when("the user enters valid credentials")
def entervalidcredentials(loginpage: Page):
    loginpage.locator("#username").fill("meghana")
    loginpage.locator("#password").fill("test123")


# Scenario action: invalid credentials
@when("the user enters invalid credentials")
def enterinvalidcredentials(loginpage: Page):
    loginpage.locator("#username").fill("wronguser")
    loginpage.locator("#password").fill("wrongpassword")


@when("the user clicks the login button")
def clicklogin(loginpage: Page):
    loginpage.locator("#login").click()


@then("the dashboard should be displayed")
def verifydashboard(loginpage: Page):
    expect(loginpage.locator("#dashboard")).to_be_visible()


@then("an error message should be displayed")
def verifyloginerror(loginpage: Page):
    expect(loginpage.locator("#error")).to_be_visible()


# Demonstrate a run-level hook using pytest's session fixture
@pytest.fixture(scope="session", autouse=True)
def testrunsetup():
    print("\nBefore all tests: Starting test run")
    yield
    print("\nAfter all tests: Test run finished")