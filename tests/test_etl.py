import io
import gzip
from pathlib import Path
from unittest.mock import patch, MagicMock

import etl.etl as etl


def test_download_and_extract_skip_if_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(etl, "DOWNLOAD_DIR", tmp_path)

    existing = tmp_path / "name.basics.tsv"
    existing.write_text("already exists")

    result = etl.download_and_extract(
        "name.basics",
        "http://example.com/file.tsv.gz"
    )

    assert result == existing
    assert existing.exists()


@patch("etl.etl.requests.get")
def test_download_and_extract_downloads(mock_get, tmp_path, monkeypatch):
    monkeypatch.setattr(etl, "DOWNLOAD_DIR", tmp_path)

    content = b"col1\tcol2\n1\t2\n"
    gz_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buffer, mode="wb") as f:
        f.write(content)

    mock_response = MagicMock()
    mock_response.iter_content.return_value = [gz_buffer.getvalue()]
    mock_response.headers = {"content-length": str(len(gz_buffer.getvalue()))}
    mock_response.__enter__.return_value = mock_response
    mock_get.return_value = mock_response

    path = etl.download_and_extract("test", "http://example.com/test.tsv.gz")

    assert path.exists()
    assert path.read_bytes() == content


def test_copy_file_to_table():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor

    fake_tsv = Path("fake.tsv")
    fake_tsv.write_text("a\tb\n1\t2\n")

    etl.copy_file_to_table(
        conn,
        fake_tsv,
        "table",
        ["a", "b"]
    )

    cursor.copy_expert.assert_called_once()
    conn.commit.assert_called_once()

    fake_tsv.unlink()


def test_prepare_schema():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor

    etl.prepare_schema(conn)

    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()
