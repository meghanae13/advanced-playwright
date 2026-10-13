from playwright.sync_api import Page


def testmockapiresponse(page: Page):
    def mockresponse(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "id": 1,
                "title": "Mock Playwright Post",
                "body": "This response comes from mocked data.",
                "userId": 1
            }
        )

    page.route("**/posts/1", mockresponse)

    page.goto("https://jsonplaceholder.typicode.com/posts/1")

    response = page.locator("body").inner_text()

    assert "Mock Playwright Post" in response
    assert "This response comes from mocked data." in response

    print("API request intercepted and mock response validated!")