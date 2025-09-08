import PyPDF2
import docx
import joblib
import os

# Load models only once at startup
MODEL_PATH = os.path.join("models", "lightgbm_ai_detector.pkl")
VECTORIZER_PATH = os.path.join("models", "tfidf_vectorizer.pkl")

lgb_model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def extract_text_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            paragraphs = [p.strip() for p in page_text.split("\n") if p.strip()]
            pages.append(paragraphs)
    return pages


def extract_text_docx(file_path, max_words=300):
    doc = docx.Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    pages, current_page, word_count = [], [], 0

    for para in paragraphs:
        words = para.split()
        n_words = len(words)

        if word_count + n_words > max_words:
            pages.append(current_page)
            current_page, word_count = [], 0

        current_page.append(para)
        word_count += n_words

    if current_page:
        pages.append(current_page)

    return pages


def smart_chunk_paragraphs_by_page(pages, min_words=200, max_words=300):
    chunks = []

    for i, page in enumerate(pages, start=1):
        current_chunk = []
        word_count = 0

        for para in page:
            words = para.split()
            n_words = len(words)

            # Split large paragraph into multiple chunks
            if n_words > max_words:
                if current_chunk:
                    chunks.append((i, " ".join(current_chunk)))
                    current_chunk = []
                    word_count = 0
                for j in range(0, n_words, max_words):
                    chunks.append((i, " ".join(words[j:j + max_words])))
                continue

            # Combine small paragraphs
            if word_count + n_words > max_words:
                chunks.append((i, " ".join(current_chunk)))
                current_chunk = []
                word_count = 0

            current_chunk.append(para)
            word_count += n_words

        if current_chunk:
            chunks.append((i, " ".join(current_chunk)))

    return chunks


def detect_ai_text(texts, model=lgb_model, vectorizer=vectorizer, threshold=0.5):
    """
    Predict whether given text(s) are AI-written or Human-written.
    texts: string or list of strings
    threshold: probability cutoff (default = 0.5)
    """
    if isinstance(texts, str):
        texts = [texts]

    X = vectorizer.transform(texts)
    probs = model.predict_proba(X)[:, 1]

    results = []
    for t, p in zip(texts, probs):
        label = "AI-generated" if p >= threshold else "Human-written"
        results.append({
            "text_preview": t[:100] + ("..." if len(t) > 100 else ""),
            "probability_AI": round(float(p), 4),
            "prediction": label
        })
    return results
