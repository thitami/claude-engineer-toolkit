"""Tests for the chunker utility."""
from __future__ import annotations
import pytest
from pathlib import Path
from cet.core.chunker import chunk_text, collect_files, read_file


def test_chunk_text_small_file():
    text = "hello world"
    chunks = chunk_text(text, max_chars=1000)
    assert chunks == ["hello world"]

def test_chunk_text_splits_large_file():
    text = ("a" * 100 + "\n\n") * 10
    chunks = chunk_text(text, max_chars=300)
    assert len(chunks) > 1

def test_chunk_text_prefers_double_newline_split():
    text = "block one\n\nblock two\n\nblock three"
    chunks = chunk_text(text, max_chars=20)
    assert all("\n\n" not in c.strip() or len(c) <= 20 for c in chunks)

def test_chunk_text_no_data_loss():
    text = "line\n" * 200
    chunks = chunk_text(text, max_chars=100)
    assert "".join(chunks).replace("\n", "") == text.replace("\n", "")

def test_collect_files_single_file(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("pass")
    result = collect_files(str(f))
    assert result == [f]

def test_collect_files_directory(tmp_path):
    (tmp_path / "a.py").write_text("pass")
    (tmp_path / "b.py").write_text("pass")
    (tmp_path / "c.txt").write_text("ignore")
    result = collect_files(str(tmp_path), extensions=[".py"])
    assert len(result) == 2
    assert all(f.suffix == ".py" for f in result)

def test_collect_files_ignores_hidden(tmp_path):
    (tmp_path / ".hidden.py").write_text("pass")
    (tmp_path / "visible.py").write_text("pass")
    result = collect_files(str(tmp_path), extensions=[".py"])
    names = [f.name for f in result]
    assert "visible.py" in names
    assert ".hidden.py" not in names

def test_read_file(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text("def hello(): pass")
    assert read_file(str(f)) == "def hello(): pass"
