from app.core.container import AppContainer


def chat(container: AppContainer, payload: dict) -> dict:
    message = payload.get("message") or payload.get("question") or ""
    response = container.agent.chat(message)
    return response.to_dict()

