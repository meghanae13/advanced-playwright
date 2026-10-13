from urllib import request

from playwright.sync_api import Page

def testapiandui(page: Page):
    response = request.get(
        "https://jsonplaceholder.typicode.com/posts/1",
        verify="/etc/ssl/certs/ca-certificates.crt",
        timeout=15
    )

    assert response.status_code == 200
    data = response.json()

    page.set_content("""
        <h1 id="title"></h1>
        <p id="body"></p>
        <p id="postid"></p>
    """)

    page.locator("#title").evaluate(
        "(element, value) => element.textContent = value",
        data["title"]
    )

    page.locator("#body").evaluate(
        "(element, value) => element.textContent = value",
        data["body"]
    )

    page.locator("#postid").evaluate(
        "(element, value) => element.textContent = value",
        str(data["id"])
    )

    assert page.locator("#title").inner_text() == data["title"]
    assert " ".join(page.locator("#body").inner_text().split()) == " ".join(data["body"].split())
    assert page.locator("#postid").inner_text() == str(data["id"])

    print("API data displayed and validated in the UI!")