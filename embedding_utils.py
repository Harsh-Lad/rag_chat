from sentence_transformers import SentenceTransformer, util
import numpy as np

class EmbeddingUtils:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, chunks):
        embeddings = self.model.encode(chunks, convert_to_tensor=True)
        return embeddings

    def find_similar_chunks(self, user_input_embedding, embeddings, chunks, k=5):
        similarities = util.pytorch_cos_sim(user_input_embedding, embeddings)[0]
        top_k = similarities.topk(k)
        similar_chunks = [chunks[idx] for idx in top_k.indices]
        return similar_chunks