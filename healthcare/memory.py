
import hashlib
import threading

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from healthcare.records import (
    get_patient,
    get_medical_history
)


_model = None
_model_lock = threading.Lock()


def get_embedding_model():
    """Load the embedding model once."""
    global _model

    with _model_lock:
        if _model is None:
            _model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

    return _model


class PatientVectorMemory:
    """
    FAISS-based semantic memory.

    Patient records are indexed separately for each
    selected patient. No patient data is sent to
    the embedding model's external API.
    """

    def __init__(self):
        self.indexes = {}
        self.documents = {}
        self.fingerprints = {}
        self.lock = threading.RLock()

    def _build_documents(self, patient_id):
        patient = get_patient(patient_id)

        if patient is None:
            return []

        records = get_medical_history(patient_id)
        documents = []

        for record in records:
            content = (
                f"Patient ID: {patient_id}\n"
                f"Record ID: {record['id']}\n"
                f"Date: {record['created_at']}\n"
                f"Diagnosis: {record['diagnosis']}\n"
                f"Treatment: {record['treatment'] or 'Not recorded'}\n"
                f"Notes: {record['notes'] or 'None'}"
            )

            documents.append({
                "record_id": record["id"],
                "patient_id": patient_id,
                "content": content
            })

        return documents

    def index_patient(self, patient_id):
        """Create or refresh one patient's vector index."""
        documents = self._build_documents(patient_id)

        fingerprint = hashlib.sha256(
            repr(documents).encode("utf-8")
        ).hexdigest()

        with self.lock:
            if self.fingerprints.get(patient_id) == fingerprint:
                return len(documents)

            if not documents:
                self.indexes.pop(patient_id, None)
                self.documents[patient_id] = []
                self.fingerprints[patient_id] = fingerprint
                return 0

            model = get_embedding_model()

            embeddings = model.encode(
                [doc["content"] for doc in documents],
                convert_to_numpy=True,
                normalize_embeddings=True
            ).astype("float32")

            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(np.ascontiguousarray(embeddings))

            self.indexes[patient_id] = index
            self.documents[patient_id] = documents
            self.fingerprints[patient_id] = fingerprint

        return len(documents)

    def search(self, patient_id, query, top_k=3):
        """Retrieve semantically relevant patient records."""
        if not query or not query.strip():
            return []

        with self.lock:
            self.index_patient(patient_id)

            documents = self.documents.get(patient_id, [])
            index = self.indexes.get(patient_id)

            if index is None or not documents:
                return []

            model = get_embedding_model()

            query_vector = model.encode(
                [query],
                convert_to_numpy=True,
                normalize_embeddings=True
            ).astype("float32")

            scores, indices = index.search(
                np.ascontiguousarray(query_vector),
                min(max(1, top_k), len(documents))
            )

            results = []

            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue

                document = documents[int(idx)]

                results.append({
                    "patient_id": patient_id,
                    "record_id": document["record_id"],
                    "content": document["content"],
                    "similarity": round(float(score), 4)
                })

            return results


patient_memory = PatientVectorMemory()


def retrieve_patient_memory(patient_id, query, top_k=3):
    """Public retrieval function for the agent."""
    return patient_memory.search(
        patient_id,
        query,
        top_k
    )


def build_rag_context(patient_id, query):
    """Build grounded context from retrieved records."""
    results = retrieve_patient_memory(
        patient_id,
        query
    )

    if not results:
        return "No relevant patient records were found."

    return "\n\n".join(
        (
            f"Source medical record #{item['record_id']}\n"
            f"{item['content']}"
        )
        for item in results
    )
