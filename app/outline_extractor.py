import fitz  # PyMuPDF
import re

def extract_headings_with_text(pdf_path, max_headings=20):
    """
    Extracts multilingual, cleaned headings (H1-H3) and page-wise text from a PDF.
    - Merges broken multi-line headings.
    - Filters out generic, very short, or low-confidence headings.
    - Keeps top `max_headings` headings per document.
    Returns:
        {
            "outline": [{"level": "H1/H2/H3", "text": str, "page": int}, ...],
            "text_by_page": {page_num: "combined text"}
        }
    """
    doc = fitz.open(pdf_path)
    fonts = []
    raw_sections = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = []
                line_font_sizes = []
                line_fonts = []
                for span in line["spans"]:
                    text = span["text"].strip()
                    # Multilingual: keep any unicode letters/numbers
                    if not text or not re.search(r'\w', text, re.UNICODE):
                        continue

                    font_size = round(span["size"], 1)
                    font_name = span.get("font", "")
                    is_bold = "Bold" in font_name or font_name.endswith("BoldMT")
                    is_caps = text.isupper() and len(text) > 3

                    line_text.append(text)
                    line_font_sizes.append(font_size)
                    line_fonts.append((font_name, is_bold, is_caps))

                    fonts.append(font_size)

                if not line_text:
                    continue

                merged_text = " ".join(line_text)
                cleaned_text = re.sub(r"[:.、।|›»→・\\-–—]+$", "", merged_text).strip()
                is_bold_line = any(b or c for _, b, c in line_fonts)

                raw_sections.append({
                    "text": cleaned_text,
                    "size": max(line_font_sizes),
                    "font": line_fonts[0][0],
                    "bold": is_bold_line,
                    "page": page_num
                })

    if not fonts:
        return {"outline": [], "text_by_page": {}}

    # Determine heading font sizes: top 3 distinct sizes
    top_sizes = sorted(set(fonts), reverse=True)[:3]
    font_map = {size: f"H{idx + 1}" for idx, size in enumerate(top_sizes)}

    # Filter and score headings by confidence
    filtered_headings = []
    for sec in raw_sections:
        text = sec["text"]
        if len(text.split()) < 3 or len(text) < 15:
            continue
        if text.lower() in ["introduction", "summary", "trip", "overview"]:
            continue

        level = font_map.get(sec["size"])
        if level and (sec["bold"] or sec["size"] == top_sizes[0]):
            confidence = sec["size"]
            if sec["bold"]:
                confidence += 2
            filtered_headings.append((confidence, {
                "level": level,
                "text": text,
                "page": sec["page"]
            }))

    filtered_headings.sort(key=lambda x: x[0], reverse=True)
    outline = [h for _, h in filtered_headings[:max_headings]]

    # Combine all page text
    doc_text = {}
    for sec in raw_sections:
        doc_text.setdefault(sec["page"], []).append(sec["text"])
    full_text = {pg: " ".join(txts) for pg, txts in doc_text.items()}

    return {"outline": outline, "text_by_page": full_text}
