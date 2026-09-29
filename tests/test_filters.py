from jobhunter.feeds import JobEntry
from jobhunter.filters import compile_keywords, matches


def entry(title="", summary="", source="feed"):
    return JobEntry(title=title, link="", summary=summary, published="", source=source, uid=title)


def test_include_keyword_matches_title_case_insensitively():
    inc = compile_keywords(["python"])
    assert matches(entry(title="Python Engineer"), inc, [])
    assert matches(entry(title="PYTHON dev"), inc, [])


def test_include_keyword_matches_summary_and_word_boundaries():
    inc = compile_keywords(["go"])
    assert matches(entry(summary="we use go here"), inc, [])
    assert not matches(entry(summary="going places"), inc, [])


def test_exclude_beats_include():
    inc = compile_keywords(["python"])
    exc = compile_keywords(["senior"])
    assert not matches(entry(title="Senior Python Engineer"), inc, exc)
    assert matches(entry(title="Junior Python Engineer"), inc, exc)


def test_empty_include_keeps_everything():
    assert matches(entry(title="Anything"), [], [])
