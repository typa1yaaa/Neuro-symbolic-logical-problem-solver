class Predicate:
    def __init__(self, quantifier=None, name=None, argument=None, negated=False):
        self.quantifier = quantifier
        self.name = name
        self.argument = argument
        self.negated = negated
    
    def to_dict(self):
        return {
            'quantifier': self.quantifier,
            'name': self.name,
            'argument': self.argument,
            'negated': self.negated
        }
    
    def to_string(self):
        """Преобразует предикат в строковое представление"""
        result = ""
        if self.negated:
            result += "¬"
        if self.quantifier:
            result += f"{self.quantifier}{self.argument}"
        if self.name:
            if '(' in self.name or self.argument:
                result += f"{self.name}({self.argument})"
            else:
                result += self.name
        return result

class LogicalExpression:
    def __init__(self):
        self.quantifiers = []
        self.operator = None
        self.expression_negated = False
        self.left = None
        self.right = None
        self.steps_log = []
    
    def to_string(self):
        """Преобразует логическое выражение в строковое представление"""
        result = ""
        
        # Отрицание всего выражения
        if self.expression_negated:
            result += "¬"
        
        # Кванторы
        for quant_type, variable in self.quantifiers:
            result += f"{quant_type}{variable}"
        
        # Если есть кванторы, добавляем скобки
        if self.quantifiers and (self.operator or self.left or self.right):
            result += "("
        
        # Левая часть
        if self.left:
            result += self.left.to_string()
        
        # Оператор
        if self.operator:
            result += f" {self.operator} "
        
        # Правая часть
        if self.right:
            result += self.right.to_string()
        
        # Закрываем скобки если были кванторы
        if self.quantifiers and (self.operator or self.left or self.right):
            result += ")"
        
        return result
