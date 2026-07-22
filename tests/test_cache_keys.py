import pytest

from packages.shared.cache_keys import RagCacheKey


def test_cache_key_includes_workspace_and_versions():
    key = RagCacheKey(
        namespace="answer",
        workspace_id="workspace-a",
        query="What is the leave policy?",
        retrieval_config_version="retrieval-v1",
        embedding_version="embedding-v1",
        index_version="index-v1",
        prompt_version="prompt-v1",
        generation_model="mock-model",
    ).build()

    assert key.startswith("answer:ws=workspace-a:")
    assert "retrieval=retrieval-v1" in key
    assert "embedding=embedding-v1" in key
    assert "index=index-v1" in key
    assert "prompt=prompt-v1" in key
    assert "model=mock-model" in key


def test_cache_key_hashes_query_and_is_workspace_isolated():
    base = dict(
        namespace="retrieval",
        query="Same query",
        retrieval_config_version="r1",
        embedding_version="e1",
        index_version="i1",
        prompt_version="p1",
        generation_model="g1",
    )

    a = RagCacheKey(workspace_id="workspace-a", **base).build()
    b = RagCacheKey(workspace_id="workspace-b", **base).build()

    assert a != b
    assert "Same query" not in a
    assert "same query" not in a


def test_cache_key_rejects_missing_workspace():
    with pytest.raises(ValueError, match="workspace_id"):
        RagCacheKey(
            namespace="answer",
            workspace_id="",
            query="question",
            retrieval_config_version="r1",
            embedding_version="e1",
            index_version="i1",
            prompt_version="p1",
            generation_model="g1",
        ).build()
