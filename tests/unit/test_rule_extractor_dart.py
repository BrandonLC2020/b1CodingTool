from b1.core.rule_extractor import RuleExtractor

def test_extract_dart_markers():
    content = """
    void main() {
      // b1:generalized:start
      // Always use sealed classes for state.
      // b1:generalized:end
      print('hello');
    }
    """
    rules = RuleExtractor().extract(content)
    assert "Always use sealed classes for state." in rules
