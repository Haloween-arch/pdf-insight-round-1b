# Adobe India Hackathon 2025 — Round 1B

## 💡 Objective

Analyze multiple PDF documents and extract the most relevant sections based on a given persona and job description. Use semantic similarity models to rank sections of PDFs and return the top-ranked relevant content.

---

## 🚀 How It Works

The system processes an input JSON file that includes:

- Persona (e.g., researcher, student)
- Job (e.g., summarization, comparison)
- Document filenames (PDFs)

For each document:

1. Extract text and headings using PyMuPDF (fitz).
2. Capture semantic meaning of each section with SentenceTransformer embeddings.
3. Score each section against the combined persona+job query using cosine similarity.
4. Rank and return the most relevant sections.

---

## 📂 Project Structure

```
app/
├── input/                       # Input folder containing PDFs + input.json
├── output/                      # Output folder containing output.json
├── main_1b.py                   # Main script to execute ranking pipeline
├── outline_extractor.py         # Extract headings and corresponding text using PyMuPDF
├── section_ranker.py            # Rank document sections using sentence-transformers
├── models/
│   └── all-MiniLM-L6-v2/        # Pre-downloaded SentenceTransformer model (~80MB)
├── requirements.txt             # Python dependencies
└── Dockerfile                   # Docker build file
```

---

## 💪 Technologies Used

- Python 3.10
- PyMuPDF for PDF parsing
- SentenceTransformers (MiniLM-L6-v2) for semantic embedding
- Torch (CPU version)
- Docker

---

## 🐳 Setup & Usage

### 1. Build Docker Image

```bash
docker build --platform linux/amd64 -t pdfoutliner:1b .
```

### 2. Prepare Input

Place your PDF files and a valid `input.json` in `app/input/`. Example `input.json`:

```json
{
  "persona": "AI Researcher",
  "job": "Looking for key findings and methods",
  "documents": ["paper1.pdf", "paper2.pdf"]
}
```

### 3. Run Container

```bash
docker run --rm ^
  -v ${PWD}/app/input:/app/input ^
  -v ${PWD}/app/output:/app/output ^
  pdfoutliner:1b
```

Note: Use `^` for PowerShell or `\` for Unix shells.

---

## 📤 Output

Results will be saved as `output.json` in the output folder. Sample structure:


---

## 🔒 License

This project is developed as part of the Adobe India Hackathon 2025 submission.