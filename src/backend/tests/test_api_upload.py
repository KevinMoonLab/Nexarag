import importlib
import sys
import types

import pytest
from fastapi import HTTPException


class FakeUploadFile:
    def __init__(self, filename, content_type, payload=b""):
        self.filename = filename
        self.content_type = content_type
        self._payload = payload

    async def read(self):
        return self._payload


def _load_upload_module(monkeypatch, llm_cls=None):
    pymupdf4llm = types.ModuleType("pymupdf4llm")
    pymupdf4llm.to_markdown = lambda _path: "# Stub PDF"

    langchain_ollama = types.ModuleType("langchain_ollama")

    class DefaultLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, _prompt):
            return "Title"

    langchain_ollama.OllamaLLM = llm_cls or DefaultLLM

    monkeypatch.setitem(sys.modules, "pymupdf4llm", pymupdf4llm)
    monkeypatch.setitem(sys.modules, "langchain_ollama", langchain_ollama)
    sys.modules.pop("api.upload", None)

    return importlib.import_module("api.upload")


def test_clean_filename_decodes_and_strips_paths(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    cleaned = upload.clean_filename("..%2F..%2Ffolder%2FMy%20Paper.pdf")

    assert cleaned == "My Paper.pdf"


def test_clean_filename_rejects_invalid_empty_name(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    with pytest.raises(ValueError, match="Invalid filename"):
        upload.clean_filename("/")


def test_sanitize_title_removes_unsafe_content_and_trims(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    title = upload.sanitize_title("  <b>Hello</b> https://example.com \x01  world  ")

    assert title == "Hello world"


def test_sanitize_title_truncates_to_100_characters(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    sanitized = upload.sanitize_title("x" * 140)

    assert len(sanitized) == 100


def test_get_file_type_from_extension(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    assert upload.get_file_type_from_extension("doc.PDF") == "application/pdf"
    assert upload.get_file_type_from_extension("notes.md") == "text/markdown"
    assert upload.get_file_type_from_extension("notes.txt") == "text/plain"
    assert upload.get_file_type_from_extension("archive.zip") == "unknown"


def test_is_allowed_file_accepts_octet_stream_with_supported_extension(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    assert upload.is_allowed_file(FakeUploadFile("paper.pdf", "application/octet-stream")) is True


def test_is_allowed_file_rejects_unknown_mime(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    assert upload.is_allowed_file(FakeUploadFile("paper.bin", "application/octet-stream")) is False
    assert upload.is_allowed_file(FakeUploadFile("paper.pdf", "image/png")) is False


def test_get_effective_content_type_uses_extension_for_octet_stream(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    assert upload.get_effective_content_type(FakeUploadFile("paper.md", "application/octet-stream")) == "text/markdown"
    assert upload.get_effective_content_type(FakeUploadFile("paper.pdf", "application/pdf")) == "application/pdf"


def test_extract_title_heuristic_prefers_markdown_heading(monkeypatch):
    upload = _load_upload_module(monkeypatch)
    content = "\n\n# Main Heading\nAuthor: someone\n"

    assert upload.extract_title_heuristic(content, "fallback.txt") == "Main Heading"


def test_extract_title_heuristic_skips_metadata_lines(monkeypatch):
    upload = _load_upload_module(monkeypatch)
    content = "Author: Jane\nemail: jane@example.com\nA usable title line\n"

    assert upload.extract_title_heuristic(content, "fallback.txt") == "A usable title line"


def test_extract_title_ollama_uses_heuristic_for_short_content(monkeypatch):
    upload = _load_upload_module(monkeypatch)
    monkeypatch.setattr(upload, "extract_title_heuristic", lambda content, filename: "heuristic-title")

    title = upload.extract_title_ollama("short content", "doc.txt", "http://ollama")

    assert title == "heuristic-title"


def test_extract_title_ollama_parses_and_sanitizes_response(monkeypatch):
    class FakeLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, _prompt):
            return 'Title: "A <b>Great</b> Paper https://bad.url"\n'

    upload = _load_upload_module(monkeypatch, llm_cls=FakeLLM)

    long_content = "This is enough content to avoid fallback. " * 5
    title = upload.extract_title_ollama(long_content, "doc.txt", "http://ollama")

    assert title == "A Great Paper"


def test_extract_title_ollama_falls_back_when_model_returns_bad_title(monkeypatch):
    class FakeLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, _prompt):
            return "I am not following your requested format"

    upload = _load_upload_module(monkeypatch, llm_cls=FakeLLM)
    monkeypatch.setattr(upload, "extract_title_heuristic", lambda content, filename: "fallback")

    long_content = "This is enough content to avoid fallback. " * 5
    title = upload.extract_title_ollama(long_content, "doc.txt", "http://ollama")

    assert title == "fallback"


def test_extract_title_ollama_falls_back_on_exception(monkeypatch):
    class ExplodingLLM:
        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, _prompt):
            raise RuntimeError("boom")

    upload = _load_upload_module(monkeypatch, llm_cls=ExplodingLLM)
    monkeypatch.setattr(upload, "extract_title_heuristic", lambda content, filename: "fallback")

    long_content = "This is enough content to avoid fallback. " * 5
    title = upload.extract_title_ollama(long_content, "doc.txt", "http://ollama")

    assert title == "fallback"


@pytest.mark.asyncio
async def test_upload_many_collects_successes_and_skips_failures(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    async def fake_upload(doc, _ollama_base_url):
        if doc.filename == "bad-http":
            raise HTTPException(status_code=400, detail="bad")
        if doc.filename == "bad-exception":
            raise RuntimeError("unexpected")
        return upload.UploadFileResponse(
            id=f"id-{doc.filename}",
            path=f"{doc.filename}.md",
            og_path=doc.filename,
            name=doc.filename,
            message="ok",
            size=1,
        )

    monkeypatch.setattr(upload, "upload", fake_upload)

    docs = [
        FakeUploadFile("good-1", "text/plain"),
        FakeUploadFile("bad-http", "text/plain"),
        FakeUploadFile("bad-exception", "text/plain"),
        FakeUploadFile("good-2", "text/plain"),
    ]

    result = await upload.upload_many(docs, "http://ollama")

    assert [item.id for item in result] == ["id-good-1", "id-good-2"]


@pytest.mark.asyncio
async def test_upload_rejects_disallowed_file_type(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    with pytest.raises(HTTPException) as exc:
        await upload.upload(FakeUploadFile("photo.png", "image/png"), "http://ollama")

    assert exc.value.status_code == 400
    assert "File type not allowed" in exc.value.detail


@pytest.mark.asyncio
async def test_upload_rejects_invalid_utf8_text_file(monkeypatch):
    upload = _load_upload_module(monkeypatch)

    with pytest.raises(HTTPException) as exc:
        await upload.upload(
            FakeUploadFile("notes.txt", "text/plain", payload=b"\xff\xfe\xfa"),
            "http://ollama",
            extraction_method="heuristic",
        )

    assert exc.value.status_code == 400
    assert "is not a valid text file" in exc.value.detail
