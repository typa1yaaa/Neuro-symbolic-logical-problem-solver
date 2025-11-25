import re

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
            if self.argument and not self.quantifier:
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
            if isinstance(self.left, (LogicalExpression, Predicate)):
                result += self.left.to_string()
            else:
                result += str(self.left)
        
        # Оператор
        if self.operator:
            result += f" {self.operator} "
        
        # Правая часть
        if self.right:
            if isinstance(self.right, (LogicalExpression, Predicate)):
                result += self.right.to_string()
            else:
                result += str(self.right)
        
        # Закрываем скобки если были кванторы
        if self.quantifiers and (self.operator or self.left or self.right):
            result += ")"
        
        return result

class FormulaParser:
    """Класс, отвечающий исключительно за парсинг логических формул"""
    
    def __init__(self):
        self.expression = LogicalExpression()
        self.max_recursion_depth = 50  # Уменьшим глубину рекурсии
    
    def parse_formula(self, formula):
        """Разбирает формулу на составляющие"""
        self.expression = LogicalExpression()
        result = self._parse_recursive(formula.strip(), depth=0)
        if isinstance(result, (LogicalExpression, Predicate)):
            self.expression = result
        return self.get_parsed_data()
    
    def _parse_recursive(self, formula, depth=0):
        """Рекурсивно разбирает формулу"""
        if depth > self.max_recursion_depth:
            raise RecursionError(f"Превышена максимальная глубина рекурсии ({self.max_recursion_depth})")
        
        current_expr = LogicalExpression()
        remaining = formula.strip()
        
        # Если строка пустая, возвращаем None
        if not remaining:
            return None
        
        # Шаг 1: Проверяем отрицание всего выражения
        if remaining.startswith('¬'):
            current_expr.expression_negated = True
            remaining = remaining[1:].strip()
        
        # Шаг 2: Извлекаем кванторы из начала (это кванторы ВСЕГО выражения)
        quantifiers_collected = []
        while remaining.startswith(('∀', '∃')):
            match = re.match(r'([∀∃])([a-z])', remaining)
            if match:
                quant_type = match.group(1)
                variable = match.group(2)
                quantifiers_collected.append((quant_type, variable))
                remaining = remaining[2:].strip()
            else:
                break
        
        # Если есть кванторы и следующая скобка, то это кванторы выражения
        if quantifiers_collected and remaining.startswith('('):
            current_expr.quantifiers = quantifiers_collected
            remaining = remaining[1:].strip()
            # Находим закрывающую скобку для кванторов
            paren_count = 1
            content_end = -1
            for i, char in enumerate(remaining):
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        content_end = i
                        break
            
            if content_end == -1:
                # Не найдена закрывающая скобка
                remaining = remaining
            else:
                remaining = remaining[:content_end].strip()
        
        # Шаг 3: Ищем главный оператор
        operators = ['→', '∧', '∨']
        found_operator = None
        paren_count = 0
        operator_pos = -1
        
        for i, char in enumerate(remaining):
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char in operators and paren_count == 0:
                found_operator = char
                operator_pos = i
                break
        
        if found_operator:
            current_expr.operator = found_operator
            
            # Разделяем на левую и правую части
            left_part = remaining[:operator_pos].strip()
            right_part = remaining[operator_pos + 1:].strip()
            
            # Рекурсивно разбираем левую и правую части
            current_expr.left = self._parse_side(left_part, depth + 1)
            current_expr.right = self._parse_side(right_part, depth + 1)
        else:
            # Одиночный предикат или выражение в скобках
            result = self._parse_side(remaining, depth + 1)
            if isinstance(result, LogicalExpression):
                # Если результат - выражение, объединяем с текущим
                if result.quantifiers:
                    current_expr.quantifiers.extend(result.quantifiers)
                current_expr.operator = result.operator
                current_expr.left = result.left
                current_expr.right = result.right
                current_expr.expression_negated = result.expression_negated
            else:
                # Если результат - предикат, помещаем в левую часть
                current_expr.left = result
        
        return current_expr
    
    def _parse_side(self, expression, depth=0):
        """Разбирает левую или правую часть выражения"""
        if depth > self.max_recursion_depth:
            raise RecursionError(f"Превышена максимальная глубина рекурсии ({self.max_recursion_depth})")
            
        expression = expression.strip()
        
        # Если строка пустая, возвращаем None
        if not expression:
            return None
        
        # Убираем внешние скобки, если они охватывают всё выражение
        while (expression.startswith('(') and expression.endswith(')') and 
               self._is_balanced_parentheses(expression[1:-1])):
            expression = expression[1:-1].strip()
        
        # Проверяем, является ли это сложным выражением
        if any(op in expression for op in ['→', '∧', '∨']):
            # Рекурсивно разбираем как выражение
            return self._parse_recursive(expression, depth + 1)
        else:
            # Это предикат (может содержать квантор предиката)
            return self._parse_predicate(expression)
    
    def _is_balanced_parentheses(self, expression):
        """Проверяет, сбалансированы ли скобки в выражении"""
        count = 0
        for char in expression:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count < 0:
                    return False
        return count == 0
    
    def _parse_predicate(self, expression):
        """Разбирает одиночный предикат (может содержать квантор предиката)"""
        predicate = Predicate()
        expr = expression.strip()
        
        # Если строка пустая, возвращаем None
        if not expr:
            return None
        
        # Проверяем отрицание
        if expr.startswith('¬'):
            predicate.negated = True
            expr = expr[1:].strip()
        
        # Проверяем, начинается ли с квантора (квантор предиката)
        if expr.startswith(('∀', '∃')):
            match = re.match(r'([∀∃])([a-z])', expr)
            if match:
                quant_type = match.group(1)
                variable = match.group(2)
                predicate.quantifier = quant_type
                # Остаток после квантора
                expr = expr[2:].strip()
        
        # Пробуем разобрать как предикат с аргументами
        match = re.match(r'([A-Za-zА-Яа-я]+)\(([^)]+)\)', expr)
        if match:
            predicate.name = match.group(1)
            predicate.argument = match.group(2)
        else:
            # Простое выражение без аргументов
            predicate.name = expr
        
        return predicate
    
    def get_parsed_data(self):
        """Возвращает структурированные данные разбора"""
        def expr_to_dict(expr):
            if isinstance(expr, LogicalExpression):
                return {
                    'type': 'expression',
                    'quantifiers': expr.quantifiers,
                    'operator': expr.operator,
                    'expression_negated': expr.expression_negated,
                    'left': expr_to_dict(expr.left) if expr.left else None,
                    'right': expr_to_dict(expr.right) if expr.right else None,
                    'steps_log': expr.steps_log
                }
            elif isinstance(expr, Predicate):
                return {
                    'type': 'predicate',
                    'quantifier': expr.quantifier,
                    'name': expr.name,
                    'argument': expr.argument,
                    'negated': expr.negated
                }
            else:
                return None
        
        return expr_to_dict(self.expression)
    
    def print_analysis(self):
        """Выводит детальный анализ формулы"""
        print("\n" + "="*50)
        print("АНАЛИЗ ФОРМУЛЫ")
        print("="*50)
        self._print_expression(self.expression)
    
    def _print_expression(self, expr, indent=0):
        """Рекурсивно выводит выражение"""
        space = "  " * indent
        
        if isinstance(expr, LogicalExpression):
            print(f"{space}ВЫРАЖЕНИЕ:")
            print(f"{space}  Кванторы ВЫРАЖЕНИЯ: {expr.quantifiers}")
            print(f"{space}  Оператор: {expr.operator}")
            print(f"{space}  Отрицание выражения: {expr.expression_negated}")
            
            if expr.left:
                print(f"{space}  Левая часть:")
                self._print_expression(expr.left, indent + 2)
            
            if expr.right:
                print(f"{space}  Правая часть:")
                self._print_expression(expr.right, indent + 2)
                
        elif isinstance(expr, Predicate):
            print(f"{space}ПРЕДИКАТ:")
            print(f"{space}  Квантор ПРЕДИКАТА: {expr.quantifier}")
            print(f"{space}  Имя: {expr.name}")
            print(f"{space}  Аргумент: {expr.argument}")
            print(f"{space}  Отрицание: {expr.negated}")

    def to_string(self):
        """Преобразует всё выражение в строковое представление"""
        if isinstance(self.expression, (LogicalExpression, Predicate)):
            return self.expression.to_string()
        return ""