from pathlib import Path

from playwright.sync_api import Page, expect


def testsinglefileupload(page: Page, tmp_path: Path):
    uploadfile = tmp_path / "resume.pdf"
    uploadfile.write_text("Sample resume content")

    page.set_content("""
        <input type="file" id="fileinput">
        <button id="upload">Upload</button>
        <p id="filename"></p>
        <p id="status"></p>

        <script>
            document.querySelector("#upload").addEventListener("click", () => {
                const file = document.querySelector("#fileinput").files[0];

                if (file && file.name.endsWith(".pdf")) {
                    document.querySelector("#filename").textContent = file.name;
                    document.querySelector("#status").textContent = "Upload successful";
                } else {
                    document.querySelector("#status").textContent = "Invalid file";
                }
            });
        </script>
    """)

    page.locator("#fileinput").set_input_files(str(uploadfile))
    page.locator("#upload").click()

    expect(page.locator("#filename")).to_have_text("resume.pdf")
    expect(page.locator("#status")).to_have_text("Upload successful")


def testmultiplefileupload(page: Page, tmp_path: Path):
    resume = tmp_path / "resume.pdf"
    certificate = tmp_path / "certificate.pdf"

    resume.write_text("Resume content")
    certificate.write_text("Certificate content")

    page.set_content("""
        <input type="file" id="files" multiple>
        <button id="upload">Upload</button>
        <ul id="filenames"></ul>

        <script>
            document.querySelector("#upload").addEventListener("click", () => {
                const list = document.querySelector("#filenames");
                list.replaceChildren();

                for (const file of document.querySelector("#files").files) {
                    const item = document.createElement("li");
                    item.textContent = file.name;
                    list.appendChild(item);
                }
            });
        </script>
    """)

    page.locator("#files").set_input_files([
        str(resume),
        str(certificate)
    ])

    page.locator("#upload").click()

    expect(page.locator("#filenames li")).to_have_count(2)
    expect(page.locator("#filenames")).to_contain_text("resume.pdf")
    expect(page.locator("#filenames")).to_contain_text("certificate.pdf")


def testinvalidfileupload(page: Page, tmp_path: Path):
    invalidfile = tmp_path / "script.exe"
    invalidfile.write_text("Sample test content")

    page.set_content("""
        <input type="file" id="fileinput">
        <button id="upload">Upload</button>
        <p id="status"></p>

        <script>
            document.querySelector("#upload").addEventListener("click", () => {
                const file = document.querySelector("#fileinput").files[0];

                if (!file || !file.name.endsWith(".pdf")) {
                    document.querySelector("#status").textContent =
                        "Only PDF files are allowed";
                } else {
                    document.querySelector("#status").textContent = "Upload successful";
                }
            });
        </script>
    """)

    page.locator("#fileinput").set_input_files(str(invalidfile))
    page.locator("#upload").click()

    expect(page.locator("#status")).to_have_text(
        "Only PDF files are allowed"
    )


def testfiledownload(page: Page, tmp_path: Path):
    downloadpath = tmp_path / "downloads" / "report.txt"
    expectedcontent = "Playwright download test report"

    page.set_content("""
        <a id="download"
           href="data:text/plain,Playwright%20download%20test%20report"
           download="report.txt">
            Download Report
        </a>
    """)

    with page.expect_download() as download_info:
        page.locator("#download").click()

    download = download_info.value

    assert download.suggested_filename == "report.txt"

    downloadpath.parent.mkdir(parents=True, exist_ok=True)
    download.save_as(str(downloadpath))

    assert downloadpath.exists()
    assert downloadpath.read_text() == expectedcontent

    print("Downloaded file:", downloadpath.name)
    print("File content:", downloadpath.read_text())