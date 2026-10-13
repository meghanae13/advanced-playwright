from pathlib import Path

from playwright.sync_api import Page, expect


# 1. Single file upload
def testsinglefileupload(page: Page, tmp_path: Path):
    uploadfile = tmp_path / "resume.pdf"
    uploadfile.write_text("Sample resume content")

    page.set_content("""
        <input type="file" id="fileinput">
        <button id="upload">Upload</button>
        <p id="filename"></p>
        <p id="status"></p>

        <script>
            document.querySelector("#upload").onclick = () => {
                const file = document.querySelector("#fileinput").files[0];

                if (file && file.name.endsWith(".pdf")) {
                    document.querySelector("#filename").textContent = file.name;
                    document.querySelector("#status").textContent = "Upload successful";
                } else {
                    document.querySelector("#status").textContent = "Invalid file";
                }
            };
        </script>
    """)

    page.locator("#fileinput").set_input_files(str(uploadfile))
    page.locator("#upload").click()

    expect(page.locator("#filename")).to_have_text("resume.pdf")
    expect(page.locator("#status")).to_have_text("Upload successful")


# 2. Multiple file upload
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
            document.querySelector("#upload").onclick = () => {
                const list = document.querySelector("#filenames");
                list.replaceChildren();

                for (const file of document.querySelector("#files").files) {
                    const item = document.createElement("li");
                    item.textContent = file.name;
                    list.appendChild(item);
                }
            };
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


# 3. Invalid extension
def testinvalidfileupload(page: Page, tmp_path: Path):
    invalidfile = tmp_path / "script.exe"
    invalidfile.write_text("Test content")

    page.set_content("""
        <input type="file" id="fileinput">
        <button id="upload">Upload</button>
        <p id="status"></p>

        <script>
            document.querySelector("#upload").onclick = () => {
                const file = document.querySelector("#fileinput").files[0];

                document.querySelector("#status").textContent =
                    file && file.name.endsWith(".pdf")
                    ? "Upload successful"
                    : "Only PDF files are allowed";
            };
        </script>
    """)

    page.locator("#fileinput").set_input_files(str(invalidfile))
    page.locator("#upload").click()

    expect(page.locator("#status")).to_have_text("Only PDF files are allowed")


# 4. Empty file validation
def testemptyfileupload(page: Page, tmp_path: Path):
    emptyfile = tmp_path / "empty.pdf"
    emptyfile.write_bytes(b"")

    page.set_content("""
        <input type="file" id="fileinput">
        <button id="upload">Upload</button>
        <p id="status"></p>

        <script>
            document.querySelector("#upload").onclick = () => {
                const file = document.querySelector("#fileinput").files[0];

                document.querySelector("#status").textContent =
                    file && file.size === 0
                    ? "Empty file not allowed"
                    : "Upload successful";
            };
        </script>
    """)

    page.locator("#fileinput").set_input_files(str(emptyfile))
    page.locator("#upload").click()

    expect(page.locator("#status")).to_have_text("Empty file not allowed")


# 5. File size validation: maximum 500 KB
def testoversizedfileupload(page: Page, tmp_path: Path):
    largefile = tmp_path / "large.pdf"
    largefile.write_bytes(b"A" * (1024 * 1024))

    page.set_content("""
        <input type="file" id="fileinput">
        <button id="upload">Upload</button>
        <p id="status"></p>

        <script>
            const maxSize = 500 * 1024;

            document.querySelector("#upload").onclick = () => {
                const file = document.querySelector("#fileinput").files[0];

                document.querySelector("#status").textContent =
                    file && file.size > maxSize
                    ? "File exceeds 500 KB"
                    : "Upload successful";
            };
        </script>
    """)

    page.locator("#fileinput").set_input_files(str(largefile))
    page.locator("#upload").click()

    expect(page.locator("#status")).to_have_text("File exceeds 500 KB")


# 6. Filename validation with special characters
def testfilenamevalidation(page: Page, tmp_path: Path):
    uploadfile = tmp_path / "resume (final) 2026.pdf"
    uploadfile.write_text("Resume content")

    page.set_content("""
        <input type="file" id="fileinput">
        <button id="upload">Upload</button>
        <p id="filename"></p>

        <script>
            document.querySelector("#upload").onclick = () => {
                const file = document.querySelector("#fileinput").files[0];
                document.querySelector("#filename").textContent =
                    file ? file.name : "";
            };
        </script>
    """)

    page.locator("#fileinput").set_input_files(str(uploadfile))
    page.locator("#upload").click()

    expect(page.locator("#filename")).to_have_text("resume (final) 2026.pdf")


# 7. File input metadata and content
def testuploadedfiledetails(page: Page, tmp_path: Path):
    uploadfile = tmp_path / "sample.txt"
    uploadfile.write_text("Playwright file test")

    page.set_content('<input type="file" id="fileinput">')
    page.locator("#fileinput").set_input_files(str(uploadfile))

    details = page.locator("#fileinput").evaluate("""
        element => ({
            name: element.files[0].name,
            size: element.files[0].size,
            count: element.files.length
        })
    """)

    assert details["name"] == "sample.txt"
    assert details["size"] == len("Playwright file test")
    assert details["count"] == 1


# 8. Download, save, filename and content validation
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
    assert download.url.startswith("data:")

    downloadpath.parent.mkdir(parents=True, exist_ok=True)
    download.save_as(str(downloadpath))

    assert downloadpath.exists()
    assert downloadpath.suffix == ".txt"
    assert downloadpath.stat().st_size > 0
    assert downloadpath.read_text() == expectedcontent
    assert download.failure() is None

    print("Downloaded:", downloadpath.name)
    print("Content:", downloadpath.read_text())


# 9. Download using a generated CSV report
def testcsvdownload(page: Page, tmp_path: Path):
    downloadpath = tmp_path / "downloads" / "employees.csv"
    expectedcontent = "id,name\n1,Meghana\n2,Tester\n"

    page.set_content("""
        <button id="download">Download CSV</button>

        <script>
            document.querySelector("#download").onclick = () => {
                const content = "id,name\\n1,Meghana\\n2,Tester\\n";
                const blob = new Blob([content], {type: "text/csv"});
                const url = URL.createObjectURL(blob);

                const link = document.createElement("a");
                link.href = url;
                link.download = "employees.csv";
                link.click();

                setTimeout(() => URL.revokeObjectURL(url), 1000);
            };
        </script>
    """)

    with page.expect_download() as download_info:
        page.locator("#download").click()

    download = download_info.value
    assert download.suggested_filename == "employees.csv"

    downloadpath.parent.mkdir(parents=True, exist_ok=True)
    download.save_as(str(downloadpath))

    assert downloadpath.exists()
    assert downloadpath.suffix == ".csv"
    assert downloadpath.read_text() == expectedcontent

    print("CSV downloaded and validated:", downloadpath.name)


# 10. Temporary file cleanup
def testfilecleanup(tmp_path: Path):
    testfile = tmp_path / "temporary.txt"
    testfile.write_text("Temporary test data")

    assert testfile.exists()

    testfile.unlink()

    assert not testfile.exists()
    print("Temporary file cleanup verified!")
