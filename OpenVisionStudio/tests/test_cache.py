from openvisionstudio.engine.cache import NodeCache


def test_cache_put_get_and_invalidate() -> None:
    cache = NodeCache()
    cache.put("n1", "abc", {"image": 1})
    assert cache.get("n1", "abc") == {"image": 1}
    assert cache.get("n1", "xyz") is None
    cache.invalidate("n1")
    assert cache.get("n1", "abc") is None
