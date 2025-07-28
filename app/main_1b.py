import os
import json
from outline_extractor import extract_headings_with_text
from section_ranker import rank_sections

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def main():
    input_file = os.path.join(INPUT_DIR, "input.json")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Missing input.json in {INPUT_DIR}")

    with open(input_file, "r", encoding="utf-8") as f:
        request = json.load(f)

    persona = request.get("persona", "").strip()
    job = request.get("job", "").strip()
    documents = request.get("documents", [])

    if not persona or not job or not documents:
        raise ValueError("Input JSON must include 'persona', 'job', and 'documents'.")

    docs_data = {}
    for pdf_file in documents:
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        if not os.path.exists(pdf_path):
            print(f"⚠ Skipping missing file: {pdf_file}")
            continue
        print(f"📄 Extracting: {pdf_file}")
        data = extract_headings_with_text(pdf_path)
        docs_data[pdf_file] = data

    if not docs_data:
        raise RuntimeError("No valid documents processed.")

    result = rank_sections(persona, job, docs_data)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Ranking completed. Results saved to {output_path}")

if __name__ == "__main__":
    main()
