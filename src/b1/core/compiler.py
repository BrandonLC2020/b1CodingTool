from pathlib import Path
from typing import List, Optional
from rich.console import Console

from b1.core.config import B1Config

console = Console()

class ContextCompiler:
    def __init__(self, project_dir: Path, config: Optional[B1Config] = None):
        self.project_dir = project_dir
        self.config = config
        
    def compile(self) -> str:
        """
        Gathers content from the root agent.md, project-specific agent.md, 
        and module context files to form a unified document.
        """
        combined = []
        
        # 0. GitHub Metadata
        if self.config and self.config.github_owner and self.config.github_repo:
            combined.append("<!-- b1CodingTool: GitHub Repository -->\n")
            combined.append("# GitHub Repository\n")
            combined.append(f"- URL: https://github.com/{self.config.github_owner}/{self.config.github_repo}\n")
            if self.config.default_branch:
                combined.append(f"- Default Branch: {self.config.default_branch}\n")
            combined.append("\n\n")

        # 1. Root agent.md
        root_agent = self.project_dir / "agent.md"
        if root_agent.exists():
            combined.append("<!-- b1CodingTool: Root Context -->\\n")
            combined.append(root_agent.read_text(encoding="utf-8").strip())
            combined.append("\\n\\n")
            
        # 2. Project-specific agent.md
        project_agent = self.project_dir / ".agent" / "project" / "agent.md"
        if project_agent.exists():
            combined.append("<!-- b1CodingTool: Project Context -->\\n")
            combined.append(project_agent.read_text(encoding="utf-8").strip())
            combined.append("\\n\\n")
            
        # 3. Installed modules' context folder
        modules_dir = self.project_dir / ".agent" / "modules"
        if modules_dir.exists():
            for mod in [d for d in modules_dir.iterdir() if d.is_dir()]:
                context_dir = mod / "context"
                if context_dir.exists():
                    for md_file in context_dir.glob("*.md"):
                        combined.append(f"<!-- b1CodingTool: Module Context [{mod.name}] - {md_file.name} -->\\n")
                        combined.append(md_file.read_text(encoding="utf-8").strip())
                        combined.append("\\n\\n")
                        
        return "".join(combined).strip()
