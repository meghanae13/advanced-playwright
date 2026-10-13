
from playwright.sync_api import Page


def testnetworkresponsestatus(page: Page):
    with page.expect_response(
        lambda response: response.url.endswith("/posts/1")
    ) as response_info:
        page.goto("https://jsonplaceholder.typicode.com/posts/1")

    response = response_info.value

    assert response.status == 200
    assert response.ok
    assert response.url.endswith("/posts/1")

    print("Status:", response.status)
    print("URL:", response.url)


def testnetworkrequestdetails(page: Page):
    with page.expect_response(
        lambda response: response.url.endswith("/posts/1")
    ) as response_info:
        page.goto("https://jsonplaceholder.typicode.com/posts/1")

    response = response_info.value
    request = response.request

    assert request.method == "GET"
    assert "jsonplaceholder.typicode.com" in request.url
    assert response.headers["content-type"].startswith("application/json")

    print("Method:", request.method)
    print("Content-Type:", response.headers["content-type"])


def testnetworkresponsebody(page: Page):
    with page.expect_response(
        lambda response: response.url.endswith("/posts/1")
    ) as response_info:
        page.goto("https://jsonplaceholder.typicode.com/posts/1")

    response = response_info.value
    data = response.json()

    assert data["id"] == 1
    assert data["userId"] == 1
    assert isinstance(data["title"], str)
    assert len(data["title"]) > 0
    assert isinstance(data["body"], str)
    assert len(data["body"]) > 0

    print("Post ID:", data["id"])
    print("Title:", data["title"])
    print("Response body validated!")