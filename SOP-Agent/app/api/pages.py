import html


PAGE_CSS = """
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#f7f8fa;color:#24292f}
main{max-width:980px;margin:0 auto;padding:28px}
nav{display:flex;gap:12px;margin-bottom:22px}
a{color:#0969da;text-decoration:none}
form{display:flex;gap:8px;margin-bottom:18px}
input,textarea{font:inherit;border:1px solid #d0d7de;border-radius:6px;padding:10px;background:white}
input{flex:1}
textarea{width:100%;min-height:86px;box-sizing:border-box}
button{border:0;border-radius:6px;padding:10px 14px;background:#0969da;color:white;font:inherit;cursor:pointer}
.result,.message,.tool{border:1px solid #d0d7de;background:white;border-radius:8px;padding:14px;margin:10px 0}
.score{color:#57606a;font-size:13px}
.tool{background:#fff8c5}
pre{white-space:pre-wrap}
"""


def layout(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{PAGE_CSS}</style>
</head>
<body>
<main>
  <nav><a href="/v1">Phase 1</a><a href="/v2">Phase 2</a><a href="/v3">Phase 3</a></nav>
  {body}
</main>
</body>
</html>"""


def search_page(title: str, api_path: str) -> str:
    safe_title = html.escape(title)
    safe_api = html.escape(api_path)
    body = f"""
<h1>{safe_title}</h1>
<form id="search-form">
  <input id="query" name="q" placeholder="输入故障关键词或问题" autofocus>
  <button type="submit">搜索</button>
</form>
<section id="results"></section>
<script>
const form = document.getElementById('search-form');
const queryInput = document.getElementById('query');
const results = document.getElementById('results');
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, ch => ({{
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}}[ch]));
form.addEventListener('submit', async (event) => {{
  event.preventDefault();
  const q = queryInput.value;
  const response = await fetch('{safe_api}?q=' + encodeURIComponent(q));
  const data = await response.json();
  results.innerHTML = data.results.map(item => `
    <article class="result">
      <h3>${{escapeHtml(item.id)}} · ${{escapeHtml(item.title)}}</h3>
      <p>${{escapeHtml(item.snippet)}}</p>
      <div class="score">score: ${{escapeHtml(item.score)}}</div>
    </article>
  `).join('') || '<p>没有结果</p>';
}});
</script>
"""
    return layout(title, body)


def chat_page() -> str:
    body = """
<h1>Phase 3：On-Call 助手 Agent</h1>
<form id="chat-form">
  <textarea id="message" placeholder="描述你的 On-Call 问题"></textarea>
  <button type="submit">发送</button>
</form>
<section id="history"></section>
<script>
const form = document.getElementById('chat-form');
const message = document.getElementById('message');
const history = document.getElementById('history');
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, ch => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[ch]));
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const content = message.value.trim();
  if (!content) return;
  history.insertAdjacentHTML('beforeend', `<article class="message"><strong>用户</strong><pre>${escapeHtml(content)}</pre></article>`);
  message.value = '';
  const response = await fetch('/v3/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: content})
  });
  const data = await response.json();
  const tools = data.tool_calls.map(call => `
    <div class="tool"><strong>${escapeHtml(call.name)}</strong>(${escapeHtml(JSON.stringify(call.arguments))})<pre>${escapeHtml(call.result_preview)}</pre></div>
  `).join('');
  history.insertAdjacentHTML('beforeend', `<article class="message"><strong>Agent</strong>${tools}<pre>${escapeHtml(data.answer)}</pre></article>`);
});
</script>
"""
    return layout("Phase 3 Agent", body)
