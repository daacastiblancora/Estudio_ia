import unittest
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

class MockVectorStore:
    def similarity_search(self, query, k):
        # Return a mix of relevant and irrelevant docs
        return [
            Document(page_content="El plazo máximo es de 15 días hábiles.", metadata={"id": 1}),
            Document(page_content="Las manzanas son rojas y deliciosas.", metadata={"id": 2}),
            Document(page_content="Para la solicitud se requiere fotocopia de cédula.", metadata={"id": 3}),
            Document(page_content="El fútbol es el deporte más popular.", metadata={"id": 4}),
            Document(page_content="Plazo de 15 días para responder.", metadata={"id": 5}),
        ]

class TestHybridLogic(unittest.TestCase):
    def test_bm25_reranking(self):
        query = "plazo máximo días"
        
        # Mock retrieval
        initial_docs = MockVectorStore().similarity_search(query, k=5)
        
        # BM25 Logic check
        tokenized_corpus = [doc.page_content.lower().split() for doc in initial_docs]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = query.lower().split()
        scores = bm25.get_scores(tokenized_query)
        
        # Sort
        scored_docs = sorted(zip(initial_docs, scores), key=lambda x: x[1], reverse=True)
        top_doc = scored_docs[0][0]
        
        print(f"Query: {query}")
        print(f"Top Result: {top_doc.page_content}")
        
        # Expecting the doc with "plazo", "máximo", "días" to be first
        self.assertIn("15 días", top_doc.page_content)

if __name__ == '__main__':
    unittest.main()
