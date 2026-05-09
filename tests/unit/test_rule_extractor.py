import pytest
from pathlib import Path
from b1.core.rule_extractor import RuleExtractor

def test_extract_rules_with_markers():
    content = """
# Project Context
Some project specific stuff.

<!-- b1:generalized:start -->
## General Rule 1
This is a general rule.
- Item 1
- Item 2
<!-- b1:generalized:end -->

More project specific stuff.

<!-- b1:generalized:start -->
## General Rule 2
Another general rule.
<!-- b1:generalized:end -->
"""
    extractor = RuleExtractor()
    rules = extractor.extract(content)
    
    assert len(rules) == 2
    assert "## General Rule 1" in rules[0]
    assert "## General Rule 2" in rules[1]

def test_extract_rules_no_markers():
    content = """
# Project Context
No general rules here.
"""
    extractor = RuleExtractor()
    rules = extractor.extract(content)
    
    assert len(rules) == 0

def test_extract_rules_with_header_fallback():
    content = """
# Project Context

## Generalized Learnings
- Always use typed parameters.
- Keep functions small.

## Project Specifics
- Port is 8080.
"""
    extractor = RuleExtractor()
    rules = extractor.extract(content)
    
    # If we decide to support header fallback
    assert len(rules) == 1
    assert "Always use typed parameters" in rules[0]
