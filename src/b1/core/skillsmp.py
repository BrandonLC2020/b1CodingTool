import httpx
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class SkillsMPSkill(BaseModel):
    id: str
    name: str
    author: str
    description: Optional[str] = None
    github_url: str = Field(..., alias="githubUrl")
    skill_url: str = Field(..., alias="skillUrl")
    stars: int = 0
    updated_at: str = Field(..., alias="updatedAt")

class SkillsMPClient:
    BASE_URL = "https://skillsmp.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def search(self, query: str, limit: int = 20) -> List[SkillsMPSkill]:
        """
        Search for skills by keyword.
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.BASE_URL}/skills/search", 
                    params={"q": query, "limit": limit},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                return [SkillsMPSkill(**s) for s in data.get("data", {}).get("skills", [])]
        except Exception as e:
            # For now, just return empty list or raise
            raise RuntimeError(f"Failed to search skillsmp.com: {e}")

    def get_by_id(self, skill_id: str) -> Optional[SkillsMPSkill]:
        """
        Find a specific skill by its ID using the search endpoint.
        """
        # Since there's no direct GET by ID, we search for the exact ID
        # We use a larger limit to ensure we find the exact ID match if it exists
        skills = self.search(skill_id, limit=50)
        for skill in skills:
            if skill.id == skill_id:
                return skill
        return None
