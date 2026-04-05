from pydantic import BaseModel, Field
import yaml
from pathlib import Path
from typing import List

class B1Config(BaseModel):
    upstream_repo: str = ""
    active_agents: List[str] = Field(default_factory=list)
    
    @classmethod
    def load(cls, project_dir: Path) -> "B1Config":
        config_path = project_dir / ".agent" / "config.yaml"
        if not config_path.exists():
            return cls()
            
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return cls(**(data or {}))
            
    def save(self, project_dir: Path):
        config_path = project_dir / ".agent" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(), f)
