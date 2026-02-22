import os
import io
import json
from datetime import datetime
import fitz  # PyMuPDF
import docx
import re
import shutil

def strip_think_tags(text: str) -> str:
    """
    Remove <think>...</think> blocks from reasoning models' outputs to prevent context pollution.
    Handles multiline and nested tag edge cases via DOTALL regex.
    """
    if not text:
        return text
    # Non-greedy match for anything between <think> and </think>
    clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return clean_text.strip()

def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
    """Extract text from a PDF file stream using PyMuPDF."""
    try:
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")

def extract_text_from_docx(file_stream: io.BytesIO) -> str:
    """Extract text from a DOCX file stream."""
    try:
        doc = docx.Document(file_stream)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Failed to parse DOCX: {str(e)}")

def extract_text_from_txt(file_stream: io.BytesIO) -> str:
    """Extract text from a TXT or Markdown file stream."""
    try:
        return file_stream.read().decode("utf-8")
    except Exception as e:
        raise Exception(f"Failed to read text file: {str(e)}")

def parse_uploaded_file(uploaded_file) -> str:
    """Router to parse uploaded Streamlit file objects based on their extension."""
    if uploaded_file is None:
        return ""
    
    filename = uploaded_file.name.lower()
    # Reset pointer before reading
    uploaded_file.seek(0)
    
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    elif filename.endswith(".md") or filename.endswith(".txt"):
        return extract_text_from_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

def truncate_text(text: str, max_chars: int = 40000) -> str:
    """
    Simple truncation strategy based on character count.
    """
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n...[Content truncated due to length limitations]..."
    return text

def create_session_folder(base_dir: str = "review_outputs") -> tuple:
    """
    Creates a new session folder and an origin_files subfolder.
    Returns (session_id, session_dir, origin_dir)
    """
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(os.getcwd(), base_dir, session_id)
    origin_dir = os.path.join(session_dir, "origin_files")
    
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(origin_dir, exist_ok=True)
    
    return session_id, session_dir, origin_dir

def save_origin_file(uploaded_file, origin_dir: str) -> str:
    """
    Saves an uploaded file to the origin_dir.
    """
    if uploaded_file is None:
        return None
    
    filepath = os.path.join(origin_dir, uploaded_file.name)
    # Reset pointer before reading bytes to save
    uploaded_file.seek(0)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.read())
    # Reset pointer again for downstream parsers just in case
    uploaded_file.seek(0)
    return filepath

def generate_output_filename(mode_name: str, paper_name: str, agent_role: str, round_num: int) -> str:
    """
    Generate standard filename: [Mode]_[Paper_Title_Prefix]_[AgentRole]_Round[N].md
    """
    mode_safe = re.sub(r'[^\w\-]', '_', mode_name)
    title_safe = re.sub(r'[^\w\-]', '_', paper_name)[:30]
    
    return f"{mode_safe}_{title_safe}_{agent_role}_Round{round_num}.md"

def save_review(session_dir: str, filename: str, content: str) -> str:
    """Save review content to the session directory."""
    filepath = os.path.join(session_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

def format_file_link(filepath: str) -> str:
    """Format an absolute filepath to a clickable markdown link or clean text."""
    # Note: Streamlit markdown can render file:// links depending on browser security policies
    # but providing the absolute path makes it copy-pasteable and clear.
    abs_path = os.path.abspath(filepath)
    return f"`{abs_path}`"

def save_metadata(session_dir: str, metadata: dict) -> str:
    """
    Saves session metadata to metadata.md.
    """
    filepath = os.path.join(session_dir, "metadata.md")
    content = "# Session Metadata\n\n"
    for key, value in metadata.items():
        if isinstance(value, dict):
            content += f"## {key}\n"
            for k, v in value.items():
                content += f"- **{k}**: {v}\n"
        elif isinstance(value, list):
            content += f"## {key}\n"
            for item in value:
                content += f"- {item}\n"
        else:
            content += f"- **{key}**: {value}\n"
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    # Also save a JSON version for programmatic parsing if ever needed
    json_filepath = os.path.join(session_dir, "metadata.json")
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
        
    return filepath
