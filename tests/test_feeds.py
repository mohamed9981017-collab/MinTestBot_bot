from jobhunter.feeds import clean_html, parse_feed

RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>Jobs</title>
  <item>
    <title>Python Backend Engineer</title>
    <link>https://example.com/1</link>
    <guid>1</guid>
    <description><![CDATA[<p>Remote <b>python</b> role</p>]]></description>
    <pubDate>Mon, 29 Sep 2026 10:00:00 GMT</pubDate>
  </item>
  <item>
    <title>Designer</title>
    <link>https://example.com/2</link>
    <guid>2</guid>
    <description>figma</description>
  </item>
</channel></rss>
"""


def test_clean_html_strips_tags_and_unescapes():
    assert clean_html("<p>Hello &amp; welcome</p>") == "Hello & welcome"
    assert clean_html("  a\n\n b ") == "a b"
    assert clean_html("") == ""


def test_parse_feed_extracts_entries():
    entries = parse_feed(RSS, source="https://example.com/rss")
    assert len(entries) == 2
    first = entries[0]
    assert first.title == "Python Backend Engineer"
    assert first.link == "https://example.com/1"
    assert first.summary == "Remote python role"
    assert first.published == "Mon, 29 Sep 2026 10:00:00 GMT"
    assert first.source == "https://example.com/rss"
    assert first.uid == "https://example.com/rss:1"


def test_parse_feed_tolerates_missing_fields():
    entries = parse_feed("<rss><channel><item></item></channel></rss>", source="s")
    assert len(entries) == 1
    assert entries[0].title == "(untitled)"
    assert entries[0].uid == "s:(untitled)"
