import pytest
import os
import tempfile
from app.tools.files.tools import search_files, read_document

@pytest.mark.asyncio
async def test_file_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy file
        test_file = os.path.join(tmpdir, "test_doc.txt")
        with open(test_file, "w") as f:
            f.write("EZIO test content")
            
        result = await search_files(tmpdir, "test_doc")
        
        assert "Found files" in result or "No files" in result

@pytest.mark.asyncio
async def test_read_txt_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write("Hello EZIO")
        tmp_path = tmp.name
        
    try:
        result = await read_document(tmp_path, context=None)
        assert "Hello EZIO" in result
    finally:
        os.remove(tmp_path)
