import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from sentence_transformers import SentenceTransformer, util
import torch
import datetime

torch.set_num_threads(1)
# Load multilingual MiniLM model (supports many languages)
model = SentenceTransformer('/app/models/all-MiniLM-L6-v2', device='cpu')

def rank_sections(persona, job, docs_data):
    query = f"{persona}. {job}"

    all_sections = []
    section_info = []

    for doc_name, data in docs_data.items():
        for section in data["outline"]:
            # Skip headings that are too generic or duplicates like "Introduction"
            if section["text"].strip().lower() in ["introduction", "overview", "summary"]:
                continue

            pg = section["page"]
            page_text = data["text_by_page"].get(pg, "")

            # Trim text: heading + first 2 sentences (~200 chars)
            trimmed_text = " ".join(page_text.split(".")[:2])[:200]

            combined = f"{section['text']}. {trimmed_text}"
            all_sections.append(combined)
            section_info.append({
                "document": doc_name,
                "page": pg,
                "section_title": section["text"],
                "refined_text": trimmed_text
            })

    if not all_sections:
        return {
            "metadata": {
                "documents": list(docs_data.keys()),
                "persona": persona,
                "job": job,
                "timestamp": datetime.datetime.utcnow().isoformat()
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }

    # Encode query + all sections in one batch
    all_texts = [query] + all_sections
    embeddings = model.encode(all_texts, convert_to_tensor=True, batch_size=64, normalize_embeddings=True)

    query_embedding = embeddings[0]
    section_embeddings = embeddings[1:]

    scores = util.cos_sim(query_embedding, section_embeddings)[0]

    scored_sections = [(float(s), info) for s, info in zip(scores, section_info)]
    scored_sections.sort(key=lambda x: x[0], reverse=True)

    # Select top 10 unique headings
    seen_titles = set()
    top_sections = []
    sub_analysis = []
    for _, sec in scored_sections:
        title_key = sec["section_title"].strip().lower()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        sec["importance_rank"] = len(top_sections) + 1
        top_sections.append({
            "document": sec["document"],
            "page": sec["page"],
            "section_title": sec["section_title"],
            "importance_rank": sec["importance_rank"]
        })
        sub_analysis.append({
            "document": sec["document"],
            "page": sec["page"],
            "refined_text": sec["refined_text"]
        })

        if len(top_sections) == 10:
            break

    return {
        "metadata": {
            "documents": list(docs_data.keys()),
            "persona": persona,
            "job": job,
            "timestamp": datetime.datetime.utcnow().isoformat()
        },
        "extracted_sections": top_sections,
        "subsection_analysis": sub_analysis
    }
