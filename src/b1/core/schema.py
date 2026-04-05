from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import yaml
from pathlib import Path

class ModuleType(str, Enum):
    cross_cutting = "cross_cutting"
    development = "development"
    deployment = "deployment"

class SkillConfig(BaseModel):
    name: str = Field(..., description="Name of the skill")
    description: Optional[str] = Field(None, description="Brief description of what this skill does")
    install_command: Optional[str] = Field(None, description="Shell command to install/prepare this skill (e.g., npx set up)")
    
class ModuleConfig(BaseModel):
    name: str
    version: str
    type: ModuleType
    description: Optional[str] = None
    skills: List[SkillConfig] = Field(default_factory=list)
    hooks: dict = Field(default_factory=dict)
    
    @classmethod
    def from_yaml(cls, filepath: Path) -> "ModuleConfig":
        if not filepath.exists():
            raise FileNotFoundError(f"Module config not found at {filepath}")
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        if not data:
            raise ValueError(f"Empty or invalid YAML at {filepath}")
            
        return cls(**data)
