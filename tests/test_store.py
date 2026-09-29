from jobhunter.store import SeenStore


def test_store_roundtrip(tmp_path):
    path = tmp_path / "seen.json"
    store = SeenStore(path)
    assert len(store) == 0
    assert not store.is_seen("a")

    store.add("a")
    store.add("b")
    store.save()

    reloaded = SeenStore(path)
    assert reloaded.is_seen("a")
    assert reloaded.is_seen("b")
    assert len(reloaded) == 2


def test_store_ignores_corrupt_file(tmp_path):
    path = tmp_path / "seen.json"
    path.write_text("not json", encoding="utf-8")
    assert len(SeenStore(path)) == 0


def test_store_missing_file_is_empty(tmp_path):
    assert len(SeenStore(tmp_path / "nope.json")) == 0
