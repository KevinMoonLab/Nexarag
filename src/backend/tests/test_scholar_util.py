import pytest

from scholar import util


def test_retry_returns_without_sleep_when_success(monkeypatch):
    sleeps = []
    monkeypatch.setattr(util.time, "sleep", lambda delay: sleeps.append(delay))

    result = util.retry(lambda: "ok")

    assert result == "ok"
    assert sleeps == []


def test_retry_retries_rate_limit_then_succeeds(monkeypatch):
    calls = {"count": 0}
    sleeps = []

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise util.RateLimitExceededError("slow down")
        return "done"

    monkeypatch.setattr(util.time, "sleep", lambda delay: sleeps.append(delay))

    assert util.retry(flaky, max_retries=5) == "done"
    assert calls["count"] == 3
    assert sleeps == [1.1, 1.1]


def test_retry_calls_callback_on_final_rate_limit(monkeypatch):
    callbacks = []
    monkeypatch.setattr(util.time, "sleep", lambda delay: None)

    def always_limited():
        raise util.RateLimitExceededError("limit")

    with pytest.raises(util.RateLimitExceededError):
        util.retry(always_limited, max_retries=2, cb=lambda err: callbacks.append(str(err)))

    assert callbacks == ["limit"]


def test_exponential_retry_uses_capped_backoff(monkeypatch):
    calls = {"count": 0}
    sleeps = []

    def flaky():
        calls["count"] += 1
        if calls["count"] < 5:
            raise util.RateLimitExceededError("limit")
        return "ok"

    monkeypatch.setattr(util.time, "sleep", lambda delay: sleeps.append(delay))

    assert util.exponential_retry(flaky, max_retries=5, base_delay=1, max_delay=4) == "ok"
    assert sleeps == [1, 2, 4, 4]


@pytest.mark.asyncio
async def test_retry_async_retries_then_returns(monkeypatch):
    calls = {"count": 0}
    sleeps = []

    async def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise util.RateLimitExceededError("limit")
        return "async-ok"

    monkeypatch.setattr(util.time, "sleep", lambda delay: sleeps.append(delay))

    result = await util.retry_async(flaky, max_retries=5, base_delay=2, max_delay=10)

    assert result == "async-ok"
    assert sleeps == [2, 4]


def test_retry_reraises_unexpected_exception():
    with pytest.raises(ValueError, match="boom"):
        util.retry(lambda: (_ for _ in ()).throw(ValueError("boom")))
