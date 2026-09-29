from jobhunter.feeds import JobEntry
from jobhunter.formatting import format_job


def test_format_includes_title_date_summary_and_link():
    entry = JobEntry(
        title="Python Engineer",
        link="https://example.com/jobs/1",
        summary="Remote role",
        published="Mon, 29 Sep 2026",
        source="feed",
        uid="1",
    )
    text = format_job(entry)
    assert "<b>Python Engineer</b>" in text
    assert "Mon, 29 Sep 2026" in text
    assert "Remote role" in text
    assert '<a href="https://example.com/jobs/1">Read more / apply</a>' in text


def test_format_escapes_html_in_title():
    entry = JobEntry(
        title="C++ <script> & more",
        link="",
        summary="",
        published="",
        source="feed",
        uid="1",
    )
    text = format_job(entry)
    assert "<script>" not in text
    assert "&lt;script&gt;" in text
    assert "&amp;" in text
