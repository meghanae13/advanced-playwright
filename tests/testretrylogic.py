
import pytest


attempts = {}


@pytest.mark.flaky(reruns=2, reruns_delay=1)
def testretryuntilsuccess():
    testname = "testretryuntilsuccess"
    attempts[testname] = attempts.get(testname, 0) + 1

    print(f"Attempt number: {attempts[testname]}")

    # Simulate a temporary failure on the first attempt.
    if attempts[testname] < 2:
        assert False, "Simulated intermittent failure"

    assert True, "Test passed after retry"


@pytest.mark.flaky(reruns=2, reruns_delay=1)
def teststabletest():
    print("Stable test executed")
    assert 2 + 2 == 4


@pytest.mark.flaky(reruns=2, reruns_delay=1)
def testpersistentfailure():
    print("This test fails on every attempt")
    assert 2 + 2 == 5

def testcommandlineretry():
    print("Testing command-line retry configuration")
    assert 2 + 2 == 5
