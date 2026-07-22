# ADR 0002: Workspace-Isolated RAG Cache Keys

Accepted: cache keys must include workspace identity, query hash, retrieval configuration version, embedding version, index version, prompt version, and generation model.

This prevents cross-workspace cache leakage and makes cached retrieval/answer artifacts reproducible across model, prompt, and index changes.
