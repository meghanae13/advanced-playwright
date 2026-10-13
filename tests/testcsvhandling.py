import csv
from pathlib import Path

from playwright.sync_api import Page, expect


TESTDATA = Path(__file__).resolve().parents[1] / "test_data" / "testdata.csv"
RESULTFILE = Path(__file__).resolve().parents[1] / "reports" / "csvresults.csv"


# 1. Read all records from CSV
def testreadcsv():
    with open(TESTDATA, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 4
    assert rows[0]["username"] == "Meghana"
    assert rows[1]["role"] == "admin"

    print("CSV records:", rows)


# 2. Run data-driven UI tests using CSV records
def testcsvdataindriven(page: Page):
    with open(TESTDATA, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        page.set_content("""
            <input id="username">
            <input id="role">
            <button id="submit">Submit</button>
            <p id="result"></p>

            <script>
                document.querySelector("#submit").addEventListener("click", () => {
                    const username =
                        document.querySelector("#username").value;
                    const role =
                        document.querySelector("#role").value;

                    let result;

                    if (!username.trim()) {
                        result = "validation";
                    } else if (
                        ["tester", "admin"].includes(role)
                    ) {
                        result = "success";
                    } else {
                        result = "failure";
                    }

                    document.querySelector("#result").textContent = result;
                });
            </script>
        """)

        page.locator("#username").fill(row["username"])
        page.locator("#role").fill(row["role"])
        page.get_by_role("button", name="Submit").click()

        actual = page.locator("#result").inner_text()
        expected = row["expected"]

        print(
            f"Username={row['username']!r}, "
            f"Expected={expected}, Actual={actual}"
        )

        assert actual == expected


# 3. Write execution results into a CSV file
def testwritecsvresults():
    RESULTFILE.parent.mkdir(parents=True, exist_ok=True)

    results = [
        ["Meghana", "success", "success", "PASS"],
        ["Pavan", "success", "success", "PASS"],
        ["InvalidUser", "failure", "failure", "PASS"],
    ]

    with open(RESULTFILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "username",
            "expected",
            "actual",
            "status",
        ])

        writer.writerows(results)

    with open(RESULTFILE, newline="", encoding="utf-8") as file:
        saved_rows = list(csv.DictReader(file))

    assert len(saved_rows) == 3
    assert saved_rows[0]["status"] == "PASS"

    print("CSV results saved to:", RESULTFILE)


# 4. Handle empty CSV values
def testcsvemptyvalues():
    with open(TESTDATA, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    empty_row = rows[3]

    username = empty_row["username"].strip()
    role = empty_row["role"].strip()

    assert username == ""
    assert role == "unknown"

    print("Empty username handled correctly.")
