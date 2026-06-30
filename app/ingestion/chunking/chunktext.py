def chunk_text(text, max_chars=2000, overlap=200):
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + max_chars
        chunks.append(text[start:end])
        start += (max_chars - overlap)
    return chunks
