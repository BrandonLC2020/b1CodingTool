import re

def extract_github_slug(input_str: str) -> tuple[str, str] | None:
    pattern = r"(?:github\.com[:/]|)([\w.-]+)/([\w.-]+?)(?:\.git|/|$)"
    match = re.search(pattern, input_str)
    if match:
        return match.group(1), match.group(2)
    return None
