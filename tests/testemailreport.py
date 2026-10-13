
import smtplib
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import MagicMock, patch


def testemailreport():
    # 1. Locate and validate the HTML report.
    reportfile = (
        Path(__file__).resolve().parents[1]
        / "reports"
        / "testreport.html"
    )

    assert reportfile.exists(), f"Report not found: {reportfile}"
    assert reportfile.stat().st_size > 0, "HTML report is empty"

    # 2. Build the email.
    message = EmailMessage()
    message["Subject"] = "Playwright Test Execution Report"
    message["From"] = "sender@example.com"
    message["To"] = "recipient@example.com"

    message.set_content(
        "Please find the attached Playwright HTML test report."
    )

    # 3. Attach the HTML report.
    report_content = reportfile.read_bytes()

    message.add_attachment(
        report_content,
        maintype="text",
        subtype="html",
        filename=reportfile.name,
    )

    # 4. Verify the email and attachment.
    assert message["Subject"] == "Playwright Test Execution Report"
    assert message["From"] == "sender@example.com"
    assert message["To"] == "recipient@example.com"

    attachments = list(message.iter_attachments())

    assert len(attachments) == 1
    assert attachments[0].get_filename() == "testreport.html"
    assert attachments[0].get_content_type() == "text/html"
    assert attachments[0].get_payload(decode=True) == report_content

    # 5. Mock SMTP; no real email will be sent.
    mock_server = MagicMock()
    mock_smtp = MagicMock()
    mock_smtp.__enter__.return_value = mock_server

    with patch("smtplib.SMTP", return_value=mock_smtp) as smtp_constructor:
        with smtplib.SMTP("localhost", 1025, timeout=5) as server:
            server.starttls()
            server.login("sender@example.com", "dummy-password")
            server.send_message(message)

        # 6. Verify the SMTP workflow.
        smtp_constructor.assert_called_once_with(
            "localhost", 1025, timeout=5
        )
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            "sender@example.com", "dummy-password"
        )
        mock_server.send_message.assert_called_once_with(message)

    print("Email construction verified.")
    print("HTML report attachment verified.")
    print("SMTP workflow verified using a mock.")
    print("No real email was sent.")
