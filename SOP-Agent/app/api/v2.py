from app.core.container import AppContainer


def search(container: AppContainer, query: str) -> dict:
    results = container.semantic_search.search(query)
    return {"query": query, "results": [result.to_dict() for result in results]}

