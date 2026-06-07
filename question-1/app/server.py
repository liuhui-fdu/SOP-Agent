import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

from app.api import v1, v2, v3
from app.api.pages import chat_page, search_page
from app.core.config import load_config
from app.core.container import AppContainer


def extract_q(raw_query: str) -> str:
    parsed = parse_qs(raw_query, keep_blank_values=True)
    value = parsed.get("q", [""])[0]
    if value == "" and raw_query == "q=&":
        return "&"
    return value


class OnCallRequestHandler(BaseHTTPRequestHandler):
    container: AppContainer

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/v1":
                self._send_html(search_page("Phase 1：关键词搜索", "/v1/search"))
            elif parsed.path == "/v2":
                self._send_html(search_page("Phase 2：语义搜索", "/v2/search"))
            elif parsed.path == "/v3":
                self._send_html(chat_page())
            elif parsed.path == "/v1/search":
                self._send_json(v1.search(self.container, extract_q(parsed.query)))
            elif parsed.path == "/v2/search":
                self._send_json(v2.search(self.container, extract_q(parsed.query)))
            elif parsed.path == "/health":
                self._send_json({"status": "ok"})
            else:
                self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/v1/documents":
                self._send_json(v1.create_document(self.container, payload), status=HTTPStatus.CREATED)
            elif parsed.path == "/v3/chat":
                self._send_json(v3.chat(self.container, payload))
            else:
                self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(int(status))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = body.encode("utf-8")
        self.send_response(int(status))
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def create_server() -> ThreadingHTTPServer:
    config = load_config()
    OnCallRequestHandler.container = AppContainer(config)
    return ThreadingHTTPServer((config.host, config.port), OnCallRequestHandler)


def main() -> None:
    server = create_server()
    host, port = server.server_address
    print(f"On-Call assistant listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
