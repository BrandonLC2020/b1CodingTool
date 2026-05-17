import re
from typing import List

class RuleExtractor:
    """
    Intelligent scanner for extracting generalized rules from markdown files.
    """
    
    # Matches blocks between <!-- b1:generalized:start --> and <!-- b1:generalized:end -->
    MARKER_REGEX = re.compile(
        r"<!-- b1:generalized:start -->\s*(.*?)\s*<!-- b1:generalized:end -->", 
        re.DOTALL
    )

    # Matches blocks between // b1:generalized:start and // b1:generalized:end
    DART_MARKER_REGEX = re.compile(
        r"//\s*b1:generalized:start\s*(.*?)\s*//\s*b1:generalized:end",
        re.DOTALL
    )
    
    # Fallback: Matches sections under "## Generalized Learnings" until the next "## " header
    FALLBACK_HEADER = "## Generalized Learnings"
    
    def extract(self, content: str) -> List[str]:
        """
        Extracts generalized rules from the provided markdown content.
        """
        rules = []
        
        # 1. Try HTML-style markers
        matches = self.MARKER_REGEX.findall(content)
        if matches:
            rules.extend([m.strip() for m in matches])
            
        # 2. Try Dart-style markers
        dart_matches = self.DART_MARKER_REGEX.findall(content)
        if dart_matches:
            for match in dart_matches:
                # Clean up "// " from each line in the match
                lines = match.strip().splitlines()
                cleaned_lines = [re.sub(r"^\s*//\s*", "", line) for line in lines]
                rules.append("\n".join(cleaned_lines).strip())

        if rules:
            return rules
            
        # 3. Try fallback header
        if self.FALLBACK_HEADER in content:
            # Find the section starting with FALLBACK_HEADER
            start_index = content.find(self.FALLBACK_HEADER)
            section_content = content[start_index + len(self.FALLBACK_HEADER):].strip()
            
            # Find the next header (## )
            next_header_match = re.search(r"\n##\s+", section_content)
            if next_header_match:
                section_content = section_content[:next_header_match.start()].strip()
            
            if section_content:
                rules.append(section_content)
                
        return rules
