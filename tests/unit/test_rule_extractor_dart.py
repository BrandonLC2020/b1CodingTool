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

def test_extract_multiple_dart_blocks():
    content = """
    // b1:generalized:start
    // Rule 1
    // b1:generalized:end
    
    void foo() {}
    
    // b1:generalized:start
    // Rule 2
    // b1:generalized:end
    """
    rules = RuleExtractor().extract(content)
    assert len(rules) == 2
    assert "Rule 1" in rules[0]
    assert "Rule 2" in rules[1]

def test_extract_indented_dart_blocks():
    content = """
    class MyWidget {
      void build() {
        //   b1:generalized:start
        //   Nested rule.
        //   b1:generalized:end
      }
    }
    """
    rules = RuleExtractor().extract(content)
    assert len(rules) == 1
    assert "Nested rule." in rules[0]
