# splits documents into section aware section into chunks(600 tokens) containing section title,source, page_hint

from transformers import AutoTokenizer

_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def chunk_document(parsed: dict, max_tokens: int = 600, overlap: int = 50) -> list:
    text   = parsed["text"]
    source = parsed["source"]
    sections = _detect_section_boundaries(text)
    
    chunks = []
    
    if sections:
        for i, (title, start) in enumerate(sections):
            end = sections[i + 1][1] if i + 1 < len(sections) else len(text)
            section_text = text[start:end].strip()
            
            # If section fits within token limit, keep whole
            tokens = _tokenizer.encode(section_text)
            if len(tokens) <= max_tokens:
                chunks.append({
                    "text":          section_text,
                    "section_title": title.strip(),
                    "source":        source,
                    "chunk_index":   len(chunks)
                })
            else:
                # Sliding window for oversized sections
                for j, sub in enumerate(_sliding_window(tokens, max_tokens, overlap)):
                    chunks.append({
                        "text":          _tokenizer.decode(sub, skip_special_tokens=True),
                        "section_title": f"{title.strip()} [part {j+1}]",
                        "source":        source,
                        "chunk_index":   len(chunks)
                    })
    else:
        # No section headers detected — pure sliding window
        tokens = _tokenizer.encode(text)
        for i, sub in enumerate(_sliding_window(tokens, max_tokens, overlap)):
            chunks.append({
                "text":          _tokenizer.decode(sub, skip_special_tokens=True),
                "section_title": f"Chunk {i+1}",
                "source":        source,
                "chunk_index":   i
            })
    
    return chunks

def _sliding_window(tokens, size, overlap):
    stride = size - overlap
    return [tokens[i:i+size] for i in range(0, len(tokens), stride)]

#for regulations mapping
def _detect_section_boundaries(text):
    import re
    patterns = [
        r"(Item\s+\d+[A-Z]?\.\s+[A-Z][^\n]{5,60})",
        r"(Article\s+\d+[\.\s][^\n]{5,60})",
        r"(§\s*\d+[\.\d]+\s+[^\n]{5,60})",
        r"(Section\s+\d+[\.\d]*\s+[^\n]{5,60})",
    ]
    combined = "|".join(patterns)
    return [(m.group(), m.start()) for m in re.finditer(combined, text)]
