
from playwright.sync_api import Page, expect


def testhomepage(page: Page):
    page.set_content("<h1>Home Page</h1>")
    expect(page.locator("h1")).to_have_text("Home Page")


def testsearch(page: Page):
    page.set_content("""
        <input id="search" placeholder="Search products">
        <button id="searchbtn">Search</button>
        <p id="result"></p>

        <script>
            document.querySelector("#searchbtn").onclick = () => {
                const value = document.querySelector("#search").value;
                document.querySelector("#result").textContent =
                    value ? "Results for " + value : "Enter a search term";
            };
        </script>
    """)

    page.locator("#search").fill("Laptop")
    page.locator("#searchbtn").click()

    expect(page.locator("#result")).to_have_text("Results for Laptop")


def testcheckbox(page: Page):
    page.set_content("""
        <input type="checkbox" id="terms">
        <label for="terms">Accept terms</label>
    """)

    page.locator("#terms").check()
    expect(page.locator("#terms")).to_be_checked()
