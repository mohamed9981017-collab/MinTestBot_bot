from jobhunter.config import Config, split_list


def test_split_list_handles_commas_newlines_and_blanks():
    assert split_list("a, b\nc ,, d") == ["a", "b", "c", "d"]
    assert split_list("") == []
    assert split_list(None) == []


def test_from_env_requires_token_and_chat_id():
    try:
        Config.from_env({})
    except ValueError as exc:
        assert "TELEGRAM_TOKEN" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    try:
        Config.from_env({"TELEGRAM_TOKEN": "t"})
    except ValueError as exc:
        assert "TELEGRAM_CHAT_ID" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_from_env_parses_values():
    cfg = Config.from_env(
        {
            "TELEGRAM_TOKEN": "tok",
            "TELEGRAM_CHAT_ID": "42",
            "RSS_FEEDS": "https://a/rss,https://b/rss",
            "JOB_KEYWORDS": "python,remote",
            "EXCLUDE_KEYWORDS": "senior",
            "POLL_INTERVAL": "60",
            "MAX_ITEMS_PER_RUN": "5",
            "DRY_RUN": "true",
            "STATE_FILE": "state.json",
        }
    )
    assert cfg.telegram_token == "tok"
    assert cfg.telegram_chat_id == "42"
    assert cfg.feeds == ["https://a/rss", "https://b/rss"]
    assert cfg.include_keywords == ["python", "remote"]
    assert cfg.exclude_keywords == ["senior"]
    assert cfg.poll_interval == 60
    assert cfg.max_items_per_run == 5
    assert cfg.dry_run is True
    assert cfg.state_file == "state.json"


def test_feeds_file_is_used_when_rss_feeds_absent(tmp_path):
    feeds_file = tmp_path / "feeds.txt"
    feeds_file.write_text("# comment\nhttps://a/rss\n\nhttps://b/rss\n", encoding="utf-8")
    cfg = Config.from_env(
        {
            "TELEGRAM_TOKEN": "tok",
            "TELEGRAM_CHAT_ID": "42",
            "RSS_FEEDS_FILE": str(feeds_file),
        }
    )
    assert cfg.feeds == ["https://a/rss", "https://b/rss"]
