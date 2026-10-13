import pytest


@pytest.fixture
def userdetails():
    print("\nSetup: Creating test user")

    user = {
        "id": 101,
        "name": "Meghana",
        "role": "tester"
    }

    yield user

    print("\nTeardown: Cleaning up test user")


def testusername(userdetails):
    assert userdetails["name"] == "Meghana"
    print("Username:", userdetails["name"])


def testuserrole(userdetails):
    assert userdetails["role"] == "tester"
    print("Role:", userdetails["role"])