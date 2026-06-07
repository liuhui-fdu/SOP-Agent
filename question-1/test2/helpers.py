import tempfile
from pathlib import Path

from app.core.config import AppConfig, AgentConfig, SearchConfig
from app.core.container import AppContainer


def make_temp_container() -> tuple[tempfile.TemporaryDirectory, AppContainer]:
    temp_dir = tempfile.TemporaryDirectory()
    data_dir = Path(temp_dir.name)
    (data_dir / "sop-001.html").write_text(
        """
        <html><head><title>后端服务 On-Call SOP</title></head>
        <body><main>
        <h1>后端服务 On-Call SOP</h1>
        <p>服务 OOM 时保存堆转储，检查 JVM 内存曲线，必要时扩容 Pod 或回滚。</p>
        <p>P0级故障需五分钟内升级到技术负责人并拉起 War Room。</p>
        </main><script>replication</script></body></html>
        """,
        encoding="utf-8",
    )
    (data_dir / "sop-002.html").write_text(
        """
        <html><head><title>数据库DBA On-Call SOP</title></head>
        <body><main><h1>数据库DBA On-Call SOP</h1>
        <p>主从延迟超过十秒触发严重告警，通过 SHOW SLAVE STATUS 检查复制错误。</p>
        </main></body></html>
        """,
        encoding="utf-8",
    )
    (data_dir / "sop-005.html").write_text(
        """
        <html><head><title>信息安全 On-Call SOP</title></head>
        <body><main><h1>信息安全 On-Call SOP</h1>
        <p>怀疑入侵时隔离主机，保全日志和系统快照，成功入侵必须立即升级。</p>
        </main></body></html>
        """,
        encoding="utf-8",
    )
    config = AppConfig(
        root_dir=Path(temp_dir.name),
        data_dir=data_dir,
        search=SearchConfig(
            top_k=10,
            semantic_concepts={
                "backend": ["服务", "OOM", "服务器", "挂了", "Pod", "P0", "升级"],
                "database": ["数据库", "主从", "延迟", "复制"],
                "security": ["黑客", "攻击", "入侵", "安全"],
            },
        ),
        agent=AgentConfig(max_steps=6),
    )
    return temp_dir, AppContainer(config)

