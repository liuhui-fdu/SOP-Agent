import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class SearchConfig:
    top_k: int = 10
    keyword_weight: float = 1.0
    semantic_weight: float = 1.0
    semantic_concepts: Dict[str, List[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentConfig:
    max_steps: int = 6
    llm_provider: str = "mock"


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path
    data_dir: Path
    host: str = "127.0.0.1"
    port: int = 8000
    search: SearchConfig = field(default_factory=SearchConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)


def load_config(path: Optional[Path] = None) -> AppConfig:
    root_dir = Path(__file__).resolve().parents[2]
    config_path = path or root_dir / "config" / "config.json"
    raw = {}
    if config_path.exists():
        raw = json.loads(config_path.read_text(encoding="utf-8"))

    data_dir = Path(os.getenv("ONCALL_DATA_DIR", raw.get("data_dir", "data")))
    if not data_dir.is_absolute():
        data_dir = root_dir / data_dir

    search_raw = raw.get("search", {})
    agent_raw = raw.get("agent", {})
    return AppConfig(
        root_dir=root_dir,
        data_dir=data_dir,
        host=os.getenv("ONCALL_HOST", raw.get("host", "127.0.0.1")),
        port=int(os.getenv("ONCALL_PORT", raw.get("port", 8000))),
        search=SearchConfig(
            top_k=int(search_raw.get("top_k", 10)),
            keyword_weight=float(search_raw.get("keyword_weight", 1.0)),
            semantic_weight=float(search_raw.get("semantic_weight", 1.0)),
            semantic_concepts=search_raw.get("semantic_concepts", {}),
        ),
        agent=AgentConfig(
            max_steps=int(agent_raw.get("max_steps", 6)),
            llm_provider=os.getenv("ONCALL_LLM_PROVIDER", agent_raw.get("llm_provider", "mock")),
        ),
    )
