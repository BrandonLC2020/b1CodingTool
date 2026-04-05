from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from typing import List, Dict

from b1.core.config import B1Config
from b1.core.compiler import ContextCompiler

app = FastAPI(title="b1CodingTool Dashboard API")

# Path to the React build artifacts
DASHBOARD_DIST = Path(__file__).parent.parent.parent.parent / "dashboard" / "dist"

@app.get("/api/project")
def get_project_info():
    project_dir = Path.cwd()
    return {
        "name": project_dir.name,
        "path": str(project_dir),
        "initialized": (project_dir / ".agent").exists()
    }

@app.get("/api/config")
def get_config():
    project_dir = Path.cwd()
    config = B1Config.load(project_dir)
    return config.model_dump()

@app.get("/api/modules")
def get_modules():
    project_dir = Path.cwd()
    modules_dir = project_dir / ".agent" / "modules"
    if not modules_dir.exists():
        return []
    
    modules = []
    for d in modules_dir.iterdir():
        if d.is_dir():
            # Basic metadata for now, could parse module.yaml here
            modules.append({
                "name": d.name,
                "status": "installed",
                "path": str(d.relative_to(project_dir))
            })
    return modules

@app.get("/api/context")
def get_compiled_context():
    project_dir = Path.cwd()
    if not (project_dir / ".agent").exists():
        raise HTTPException(status_code=400, detail="Project not initialized")
    
    compiler = ContextCompiler(project_dir)
    return {"content": compiler.compile()}

# Serve static files if the dist directory exists
if DASHBOARD_DIST.exists():
    app.mount("/", StaticFiles(directory=str(DASHBOARD_DIST), html=True), name="static")
else:
    @app.get("/")
    def root_no_dist():
        return {"message": "Welcome to b1CodingTool API. Dashboard not built yet. Run 'npm run build' in the dashboard directory."}
