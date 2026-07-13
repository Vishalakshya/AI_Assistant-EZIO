import os
import shutil
import PyPDF2
import docx
from typing import List, Dict, Any
from app.core.interfaces.base import FileSystemInterface

class WindowsFileSystem(FileSystemInterface):
    def search_files(self, query: str, path: str = None, recursive: bool = True) -> List[str]:
        # Default to User directory if no path provided
        start_path = path if path else os.path.expanduser("~")
        results = []
        
        if recursive:
            for root, dirs, files in os.walk(start_path):
                # Basic protection against traversing massive system directories
                if "AppData" in root or "Windows" in root:
                    continue
                for file in files:
                    if query.lower() in file.lower():
                        results.append(os.path.join(root, file))
                    if len(results) >= 20: # Limit results
                        return results
        else:
            if os.path.exists(start_path):
                for file in os.listdir(start_path):
                    if query.lower() in file.lower():
                        results.append(os.path.join(start_path, file))
        return results

    def move_file(self, source: str, destination: str) -> bool:
        if not os.path.exists(source):
            return False
        try:
            shutil.move(source, destination)
            return True
        except Exception:
            return False

    def delete_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            return True
        except Exception:
            return False
            
    def read_pdf(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return "File not found."
        try:
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages[:10]: # Read up to 10 pages to avoid token limit
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"

    def read_docx(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return "File not found."
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs[:50]])
            return text
        except Exception as e:
            return f"Error reading DOCX: {e}"
