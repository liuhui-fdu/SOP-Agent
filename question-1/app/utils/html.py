import html


def decode_html_entities(value: str) -> str:
    return html.unescape(value or "")

