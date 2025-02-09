def bracket_convert(char) -> str:
    """
    Transform a bracket to its opposite bracket.
    """
    if char == '(':
        return ')'
    elif char == ')':
        return '('
    elif char == '[':
        return ']'
    elif char == ']':
        return '['
    elif char == '{':
        return '}'
    elif char == '}':
        return '{'
    else:
        raise ValueError("Input character is not a bracket")

def is_cjk(char):
    if '\u4e00' <= char <= '\u9fff':
        return True
    else:
        return False

class Stack(object):
    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        else:
            raise IndexError("Stack is empty")

    def peek(self):
        if self.stack:
            return self.stack[-1]

    def is_empty(self):
        return not bool(self.stack)

    def size(self):
        return len(self.stack)