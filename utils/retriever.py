def retrieve(query, model, index, chunks, k=3):
    q_vec = model.encode([query])
    distances, indices = index.search(q_vec, k)

    results = [chunks[i] for i in indices[0]]
    return results