def bracket_convert(char) -> str:
    """
    将左括号转换为右括号
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
        raise ValueError("不是括号")


class Stack(object):
    def __init__(self):
        """
        创建一个Stack类
        对栈进行初始化参数设计
        """
        self.stack = [] #存放元素的栈

    def push(self, data):
        """
        压入 push ：将新元素放在栈顶
        当新元素入栈时，栈顶上移，新元素放在栈顶。
        """
        self.stack.append(data)

    def pop(self):
        """
        弹出 pop ：从栈顶移出一个数据
        - 栈顶元素拷贝出来
        - 栈顶下移
        - 拷贝出来的栈顶作为函数返回值
        """
        # 判断是否为空栈
        if self.stack:
            return self.stack.pop()
        else:
            raise IndexError("从空栈执行弹栈操作")

    def peek(self):
        """
        查看栈顶的元素
        """
        # 判断栈是否为空
        if self.stack:
            return self.stack[-1]

    def is_empty(self):
        """
        判断栈是否为空
        """
        # 栈为非空时，self.stack为True，再取反，为False
        return not bool(self.stack)

    def size(self):
        """
        返回栈的大小
        """
        return len(self.stack)