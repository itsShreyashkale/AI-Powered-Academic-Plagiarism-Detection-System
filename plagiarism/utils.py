import os
import re
import logging
from difflib import SequenceMatcher

# NLP / ML libs
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# nltk utilities
import nltk

# try to import heavy third-party libs and fail gracefully
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

# Ensure necessary nltk resources are available (quietly)
# We attempt downloads but wrap in try/except to avoid hard crash in offline envs.
try:
    nltk.data.find("tokenizers/punkt")
except Exception:
    try:
        nltk.download("punkt", quiet=True)
    except Exception:
        pass

try:
    nltk.data.find("corpora/wordnet")
except Exception:
    try:
        nltk.download("wordnet", quiet=True)
    except Exception:
        pass

try:
    nltk.data.find("corpora/stopwords")
except Exception:
    try:
        nltk.download("stopwords", quiet=True)
    except Exception:
        pass

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize

# configure logger
logger = logging.getLogger(__name__)

# preprocessing helpers
STOP_WORDS = set(stopwords.words("english")) if 'stopwords' in nltk.corpus.__dict__ else set()
LEMMATIZER = WordNetLemmatizer()

# Lazy-loaded BERT model container
_BERT_MODEL = None


def get_bert_model(model_name: str = "all-MiniLM-L6-v2"):
    """
    Lazy-load SentenceTransformer model. Calling this repeatedly returns the cached model.
    """
    global _BERT_MODEL
    if _BERT_MODEL is None:
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is not installed. Install 'sentence-transformers' to use BERT features.")
        try:
            _BERT_MODEL = SentenceTransformer(model_name)
        except Exception as e:
            logger.exception("Failed to load SentenceTransformer model '%s': %s", model_name, e)
            raise
    return _BERT_MODEL


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from .txt and .pdf files. Returns an empty string for unsupported formats or on error.
    """
    text = ""
    if not file_path:
        return text

    try:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif ext == ".pdf":
            if PdfReader is None:
                logger.error("pypdf not installed — cannot read PDF %s", file_path)
                return ""
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                pages = []
                for page in reader.pages:
                    try:
                        pages.append(page.extract_text() or "")
                    except Exception:
                        # some pages may fail text extraction, skip them
                        logger.debug("Failed to extract text from a PDF page in %s", file_path)
                text = "\n".join(pages)
        else:
            # unsupported file type — return empty for now
            logger.debug("Unsupported file extension '%s' for file: %s", ext, file_path)
            text = ""
    except Exception as e:
        logger.exception("Error extracting text from file %s: %s", file_path, e)
        text = ""
    return text or ""


def _normalize_sentence(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def extract_matching_sentences(doc1: str, doc2: str, threshold: float = 0.8):
    """
    Return a list of matching sentence pairs between doc1 and doc2.
    Each match is a dict: {'doc1': <sentence>, 'doc2': <sentence>, 'score': <similarity>}

    Uses nltk.sent_tokenize for robust splitting and difflib.SequenceMatcher for fuzzy matching.
    Ignores very short sentences.
    """
    matches = []
    if not doc1 or not doc2:
        return matches

    try:
        sents1 = [ _normalize_sentence(s) for s in sent_tokenize(doc1) if s and len(s.strip()) > 10 ]
        sents2 = [ _normalize_sentence(s) for s in sent_tokenize(doc2) if s and len(s.strip()) > 10 ]
    except Exception:
        # fallback to naive split if sent_tokenize fails
        sents1 = [ _normalize_sentence(s) for s in doc1.split(".") if s and len(s.strip()) > 10 ]
        sents2 = [ _normalize_sentence(s) for s in doc2.split(".") if s and len(s.strip()) > 10 ]

    for s1 in sents1:
        best_score = 0.0
        best_match = None
        for s2 in sents2:
            # compute normalized similarity
            score = SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = s2
        if best_score >= threshold and best_match:
            matches.append({"doc1": s1, "doc2": best_match, "score": round(best_score, 4)})
    return matches


def preprocess_text(text: str) -> str:
    """
    Basic preprocessing:
      - remove non-letter characters (keeps spacing)
      - lower-case
      - remove stopwords
      - lemmatize
    Returns cleaned string.
    """
    if not text:
        return ""
    # keep only letters and spaces
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    words = text.lower().split()
    # remove stopwords and very short tokens
    tokens = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    tokens = [LEMMATIZER.lemmatize(w) for w in tokens]
    return " ".join(tokens)


def calculate_similarity(new_doc: str, existing_docs: list, max_features: int = 20000):
    """
    TF-IDF + cosine similarity.
    Returns the maximum similarity in [0.0, 1.0] between new_doc and any of existing_docs.
    If existing_docs is empty, returns 0.0.
    """
    try:
        if not new_doc:
            return 0.0
        if not existing_docs:
            return 0.0

        # Preprocess texts
        docs = [preprocess_text(new_doc)] + [preprocess_text(d) for d in existing_docs]

        # Edge-case: if all docs become empty after preprocessing, return 0
        if all(not d.strip() for d in docs):
            return 0.0

        # Vectorize (we instantiate vectorizer per-call to avoid vocab leakage across calls)
        vectorizer = TfidfVectorizer(stop_words="english", max_features=max_features)
        tfidf_matrix = vectorizer.fit_transform(docs)

        # Compute cosine similarity between new_doc (row 0) and others
        if tfidf_matrix.shape[0] < 2:
            return 0.0

        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        if sim.size == 0:
            return 0.0
        # ensure numeric
        result = float(np.max(sim))
        if np.isnan(result) or result is None:
            return 0.0
        return max(0.0, min(1.0, result))
    except Exception as e:
        logger.exception("TF-IDF similarity computation failed: %s", e)
        return 0.0


def calculate_semantic_similarity(new_doc: str, existing_docs: list, model_name: str = "all-MiniLM-L6-v2", batch_size: int = 32):
    """
    Compute semantic similarity using SentenceTransformer embeddings.
    Returns max cosine similarity in [0.0, 1.0].
    Uses batching for efficiency and avoid GPU-only tensors (returns numpy arrays).
    """
    try:
        if not new_doc:
            return 0.0
        if not existing_docs:
            return 0.0
        model = get_bert_model(model_name)

        # encode returns numpy arrays when convert_to_numpy=True
        texts = [new_doc] + list(existing_docs)
        embeddings = model.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False)

        # Compute cosine similarities between embeddings[0] and embeddings[1:]
        new_vec = embeddings[0]
        other_vecs = embeddings[1:]
        # guard shapes
        if other_vecs.shape[0] == 0:
            return 0.0

        # normalize to avoid numeric issues
        norm_other = np.linalg.norm(other_vecs, axis=1)
        norm_new = np.linalg.norm(new_vec)
        # avoid divide-by-zero
        norm_other[norm_other == 0] = 1e-10
        if norm_new == 0:
            norm_new = 1e-10

        cosine_scores = np.dot(other_vecs, new_vec) / (norm_other * norm_new)
        max_score = float(np.max(cosine_scores))
        if np.isnan(max_score):
            return 0.0
        return max(0.0, min(1.0, max_score))
    except Exception as e:
        logger.exception("BERT semantic similarity computation failed: %s", e)
        return 0.0
