from pathlib import Path

from playwright.sync_api import Browser, Page, expect


# 1. Open a new page using context.expect_page()
def testnewpage(context):
    main_page = context.new_page()

    main_page.set_content("""
        <a href="about:blank" target="_blank">
            Open Documentation
        </a>
    """)

    with context.expect_page() as page_info:
        main_page.get_by_role("link", name="Open Documentation").click()

    help_page = page_info.value
    help_page.set_content("<h1>Documentation</h1>")

    expect(
        help_page.get_by_role("heading", name="Documentation")
    ).to_be_visible()

    assert len(context.pages) == 2
    print("New page URL:", help_page.url)

# 2. Open and validate a popup using page.expect_popup()
def testpopup(page: Page):
    page.set_content("""
        <button onclick="window.open('about:blank', '_blank')">
            Open Help
        </button>
    """)

    with page.expect_popup() as popup_info:
        page.get_by_role("button", name="Open Help").click()

    help_page = popup_info.value
    help_page.set_content("<h1>Help Center</h1>")

    expect(
        help_page.get_by_role("heading", name="Help Center")
    ).to_be_visible()

    print("Popup URL:", help_page.url)

# 3. Access all pages and interact with each page
def testmultiplepages(context):
    main_page = context.new_page()
    main_page.set_content("<h1>Main Application</h1>")

    docs_page = context.new_page()
    docs_page.set_content("<h1>Documentation</h1>")

    payment_page = context.new_page()
    payment_page.set_content("<h1>Payment</h1>")

    pages = context.pages

    assert len(pages) == 3

    expect(pages[0].get_by_role("heading", name="Main Application")).to_be_visible()
    expect(pages[1].get_by_role("heading", name="Documentation")).to_be_visible()
    expect(pages[2].get_by_role("heading", name="Payment")).to_be_visible()

    print("Number of open pages:", len(pages))


# 4. Validate page URL, title, and content
def testpageinformation(page: Page):
    page.set_content("""
        <title>Documentation Portal</title>
        <h1>Playwright Documentation</h1>
        <p>Learn browser automation.</p>
    """)

    expect(page).to_have_title("Documentation Portal")
    expect(page.get_by_role("heading", name="Playwright Documentation")).to_be_visible()
    expect(page.locator("p")).to_have_text("Learn browser automation.")

    assert page.url.startswith("about:blank")

    print("Page title:", page.title())
    print("Page URL:", page.url)


# 5. Switch between pages using Page objects
def testswitchbetweenpages(context):
    main_page = context.new_page()
    main_page.set_content("<h1>Main Page</h1>")

    help_page = context.new_page()
    help_page.set_content("<h1>Help Page</h1>")

    # Interact with the help page directly.
    expect(help_page.get_by_role("heading", name="Help Page")).to_be_visible()

    # Return to the original page using its Page object.
    expect(main_page.get_by_role("heading", name="Main Page")).to_be_visible()

    print("Both pages are independently accessible.")


# 6. Handle multiple popups
def testmultiplepopups(page: Page, context):
    page.set_content("""
        <button onclick="window.open('about:blank', '_blank')">
            Open Docs
        </button>

        <button onclick="window.open('about:blank', '_blank')">
            Open Support
        </button>
    """)

    with page.expect_popup() as docs_info:
        page.get_by_role("button", name="Open Docs").click()

    docs_page = docs_info.value
    docs_page.set_content("<h1>Docs</h1>")

    with page.expect_popup() as support_info:
        page.get_by_role("button", name="Open Support").click()

    support_page = support_info.value
    support_page.set_content("<h1>Support</h1>")

    expect(docs_page.get_by_role("heading", name="Docs")).to_be_visible()
    expect(
        support_page.get_by_role("heading", name="Support")
    ).to_be_visible()

    assert len(context.pages) == 3

# 7. Close a page and validate the remaining pages
def testclosepage(context):
    main_page = context.new_page()
    help_page = context.new_page()

    assert len(context.pages) == 2

    help_page.close()

    assert help_page.is_closed()
    assert len(context.pages) == 1
    assert not main_page.is_closed()

    print("Closed help page; main page remains open.")


# 8. Distinguish same-page navigation from opening a new tab
def testsamepagenavigation(page: Page, context):
    page.set_content("""
        <a href="#destination">Navigate Here</a>
        <h1 id="destination">New Location</h1>
    """)

    original_page_count = len(context.pages)

    page.get_by_role("link", name="Navigate Here").click()

    expect(
        page.get_by_role("heading", name="New Location")
    ).to_be_visible()

    assert len(context.pages) == original_page_count
    assert page.url.endswith("#destination")

    print("Navigation happened in the same page.")
    
# 9. Verify pages share context-level session state
def testpagesharecontext(context):
    first_page = context.new_page()

    first_page.goto("https://example.com")
    first_page.evaluate("localStorage.setItem('testkey', 'shared-value')")

    second_page = context.new_page()
    second_page.goto("https://example.com")

    value = second_page.evaluate("localStorage.getItem('testkey')")

    assert value == "shared-value"

    print("Local storage is shared between pages in the same origin.")


# 10. Verify separate browser contexts are isolated
def testseparatecontexts(browser: Browser):
    context1 = browser.new_context()
    context2 = browser.new_context()

    try:
        page1 = context1.new_page()
        page2 = context2.new_page()

        page1.goto("https://example.com")
        page2.goto("https://example.com")

        page1.evaluate("localStorage.setItem('sessionkey', 'context-one')")

        value = page2.evaluate("localStorage.getItem('sessionkey')")

        assert value is None

        print("Separate contexts have isolated local storage.")

    finally:
        context1.close()
        context2.close()