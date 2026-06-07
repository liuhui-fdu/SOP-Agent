from app.core.container import AppContainer


def create_document(container: AppContainer, payload: dict) -> dict:
    document = container.repository.upsert_html(payload["id"], payload["html"])
    container.reindex()
    return {"id": document.id, "title": document.title}


def search(container: AppContainer, query: str) -> dict:
    results = container.keyword_search.search(query)
    return {"query": query, "results": [result.to_dict() for result in results]}

