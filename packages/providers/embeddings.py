import hashlib, math
class EmbeddingProvider:
    model='mock-embedding-v1'; version='2026-07-22'; dimensions=64
    def embed(self, text: str)->list[float]: raise NotImplementedError
class HashEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str)->list[float]:
        v=[0.0]*self.dimensions
        for token in text.lower().split(): v[int(hashlib.sha256(token.encode()).hexdigest(),16)%self.dimensions]+=1.0
        n=math.sqrt(sum(x*x for x in v)) or 1.0
        return [x/n for x in v]
def get_embedding_provider(): return HashEmbeddingProvider()
