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

class LogicalExpression:
    def __init__(self):
        self.quantifiers = []
        self.operator = None
        self.expression_negated = False
        self.left = None
        self.right = None
        self.steps_log = []

class ResolutionPreprocessor:
    def __init__(self):
        self.expression = LogicalExpression()
        self.variable_map = {}
    
    def parse_formula(self, formula):
        """Разбирает формулу на составляющие"""
        self.expression = LogicalExpression()
        self.variable_map = {}
        return self._parse_recursive(formula.strip())
    
    def _parse_recursive(self, formula):
        """Рекурсивно разбирает формулу"""
        current_expr = LogicalExpression()
        remaining = formula.strip()
        
        # Шаг 1: Проверяем отрицание всего выражения
        if remaining.startswith('¬'):
            current_expr.expression_negated = True
            remaining = remaining[1:].strip()
        
        # Шаг 2: Извлекаем кванторы из начала
        while remaining.startswith(('∀', '∃')):
            match = re.match(r'([∀∃])([a-z])', remaining)
            if match:
                quant_type = match.group(1)
                variable = match.group(2)
                
                next_char_index = 2
                if next_char_index < len(remaining) and remaining[next_char_index] == '(':
                    content_start = next_char_index
                    paren_count = 0
                    content_end = -1
                    for i in range(content_start, len(remaining)):
                        if remaining[i] == '(':
                            paren_count += 1
                        elif remaining[i] == ')':
                            paren_count -= 1
                            if paren_count == 0:
                                content_end = i
                                break
                    
                    if content_end == -1:
                        break
                    
                    content = remaining[content_start + 1:content_end]
                    current_expr.quantifiers.append((quant_type, variable))
                    remaining = content
                else:
                    break
            else:
                break
        
        # Шаг 3: Ищем главный оператор
        operators = ['→', '∧', '∨']
        found_operator = None
        paren_count = 0
        
        for i, char in enumerate(remaining):
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char in operators and paren_count == 0:
                found_operator = char
                break
        
        if found_operator:
            current_expr.operator = found_operator
            left_part, right_part = remaining.split(found_operator, 1)
            current_expr.left = self._parse_side(left_part.strip())
            current_expr.right = self._parse_side(right_part.strip())
        else:
            current_expr.left = self._parse_side(remaining.strip())
        
        self.expression = current_expr
        return self.get_parsed_data()
    
    def _parse_side(self, expression):
        """Разбирает левую или правую часть выражения"""
        expression = expression.strip()
        
        if expression.startswith('(') and expression.endswith(')'):
            expression = expression[1:-1].strip()
        
        if any(op in expression for op in ['→', '∧', '∨']):
            return self._parse_recursive(expression)
        else:
            return self._parse_predicate(expression)
    
    def _parse_predicate(self, expression):
        """Разбирает одиночный предикат"""
        predicate = Predicate()
        expr = expression.strip()
        
        if expr.startswith('¬'):
            predicate.negated = True
            expr = expr[1:].strip()
        
        if expr.startswith(('∀', '∃')):
            match = re.match(r'([∀∃])([a-z])', expr)
            if match:
                quant_type = match.group(1)
                variable = match.group(2)
                predicate.quantifier = quant_type
                expr = expr[2:].strip()
        
        match = re.match(r'([^(]+)\(([^)]+)\)', expr)
        if match:
            predicate.name = match.group(1)
            predicate.argument = match.group(2)
        else:
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
            print(f"{space}  Кванторы: {expr.quantifiers}")
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
            print(f"{space}  Квантор: {expr.quantifier}")
            print(f"{space}  Имя: {expr.name}")
            print(f"{space}  Аргумент: {expr.argument}")
            print(f"{space}  Отрицание: {expr.negated}")

    def step1_pnf(self):
        """Шаг 1 ПНФ: Устранение импликаций и обработка отрицаний"""
        if self.expression.operator == "→":
            self.expression.operator = "∨"
            if isinstance(self.expression.left, Predicate):
                self.expression.left.negated = not self.expression.left.negated
            elif isinstance(self.expression.left, LogicalExpression):
                self.expression.left.expression_negated = not self.expression.left.expression_negated

        if self.expression.expression_negated:
            self.expression.expression_negated = False
            if self.expression.operator:
                self.expression.operator = '∧' if self.expression.operator == '∨' else '∨'
            
            new_quantifiers = []
            for quant_type, variable in self.expression.quantifiers:
                new_quantifiers.append(('∃' if quant_type == '∀' else '∀', variable))
            self.expression.quantifiers = new_quantifiers
            
            if self.expression.left:
                self._invert_expression_parts(self.expression.left)
            if self.expression.right:
                self._invert_expression_parts(self.expression.right)

    def _invert_expression_parts(self, expr):
        """Рекурсивно инвертирует операторы и отрицания"""
        if isinstance(expr, Predicate):
            expr.negated = not expr.negated
        elif isinstance(expr, LogicalExpression):
            if expr.operator:
                expr.operator = '∧' if expr.operator == '∨' else '∨'
            if expr.left:
                self._invert_expression_parts(expr.left)
            if expr.right:
                self._invert_expression_parts(expr.right)

    def standardize_variables(self, clause_index):
        """
        Стандартизация переменных: делает все имена переменных уникальными
        clause_index - номер клоза для создания уникальных имен
        """
        variable_counter = 1
        self.variable_map = {}
        
        def standardize_recursive(expr, quantifier_scope=None):
            nonlocal variable_counter
            if quantifier_scope is None:
                quantifier_scope = set()
            
            if isinstance(expr, LogicalExpression):
                new_quantifiers = []
                for quant_type, old_var in expr.quantifiers:
                    new_var = f"x_{clause_index}_{variable_counter}"
                    variable_counter += 1
                    self.variable_map[old_var] = new_var
                    new_quantifiers.append((quant_type, new_var))
                    quantifier_scope.add(new_var)
                expr.quantifiers = new_quantifiers
                
                if expr.left:
                    standardize_recursive(expr.left, quantifier_scope.copy())
                if expr.right:
                    standardize_recursive(expr.right, quantifier_scope.copy())
                    
            elif isinstance(expr, Predicate):
                if expr.quantifier and expr.argument:
                    old_var = expr.argument
                    if re.match(r'^[a-z]$', old_var):
                        new_var = f"x_{clause_index}_{variable_counter}"
                        variable_counter += 1
                        self.variable_map[old_var] = new_var
                        expr.argument = new_var
                        quantifier_scope.add(new_var)
                
                if expr.argument:
                    args = [arg.strip() for arg in expr.argument.split(',')]
                    new_args = []
                    for arg in args:
                        if re.match(r'^[a-z]$', arg) and arg in self.variable_map:
                            new_args.append(self.variable_map[arg])
                        else:
                            new_args.append(arg)
                    expr.argument = ','.join(new_args)
        
        print("Запуск стандартизации переменных...")
        standardize_recursive(self.expression)
        print(f"Создано отображение переменных: {self.variable_map}")
        return self.variable_map

    def move_quantifiers_left(self):
        """
        Выносит кванторы влево, сохраняя их последовательность
        """
        def extract_quantifiers(expr):
            if isinstance(expr, LogicalExpression):
                quantifiers = expr.quantifiers.copy()
                expr.quantifiers = []
                
                left_quantifiers = []
                right_quantifiers = []
                
                if expr.left:
                    left_result = extract_quantifiers(expr.left)
                    left_quantifiers = left_result['quantifiers']
                    expr.left = left_result['expression']
                
                if expr.right:
                    right_result = extract_quantifiers(expr.right)
                    right_quantifiers = right_result['quantifiers']
                    expr.right = right_result['expression']
                
                all_quantifiers = quantifiers + left_quantifiers + right_quantifiers
                return {'quantifiers': all_quantifiers, 'expression': expr}
            
            elif isinstance(expr, Predicate):
                quantifiers = []
                if expr.quantifier:
                    quantifiers.append((expr.quantifier, expr.argument))
                    expr.quantifier = None
                return {'quantifiers': quantifiers, 'expression': expr}
            
            return {'quantifiers': [], 'expression': expr}
        
        def rebuild_expression(quantifiers, inner_expr):
            if not quantifiers:
                return inner_expr
            
            current_expr = inner_expr
            for quant_type, var in reversed(quantifiers):
                new_expr = LogicalExpression()
                new_expr.quantifiers = [(quant_type, var)]
                new_expr.left = current_expr
                current_expr = new_expr
            
            return current_expr
        
        print("Вынесение кванторов влево...")
        result = extract_quantifiers(self.expression)
        self.expression = rebuild_expression(result['quantifiers'], result['expression'])
        return self.expression

    def prepare_for_resolution(self, clause_index):
        """
        Полная подготовка к резолюции: ПНФ + вынесение кванторов + стандартизация
        """
        print("\n" + "="*70)
        print("ПОЛНАЯ ПОДГОТОВКА К РЕЗОЛЮЦИИ")
        print("="*70)
        
        # Шаг 1: Устранение импликаций и отрицаний
        print("\n1. УСТРАНЕНИЕ ИМПЛИКАЦИЙ И ОБРАБОТКА ОТРИЦАНИЙ:")
        self.step1_pnf()
        self.print_analysis()
        
        # Шаг 2: Вынесение кванторов влево
        print("\n2. ВЫНЕСЕНИЕ КВАНТОРОВ ВЛЕВО:")
        self.move_quantifiers_left()
        self.print_analysis()
        
        # Шаг 3: Стандартизация переменных
        print("\n3. СТАНДАРТИЗАЦИЯ ПЕРЕМЕННЫХ:")
        self.standardize_variables(clause_index)
        self.print_analysis()
        
        return self.variable_map

# Тестируем
if __name__ == "__main__":
    test_cases = [
        "∃xЧеловек(x)",
        "∀xЧеловек(x)", 
        "∃x(Человек(x))",
        "∀x(Человек(x))",
        "¬Человек(Сократ)",
        "∀x(Человек(x)→Смертен(x))",
        "¬∀x(Человек(x)→Смертен(x))",
        "∀x(Человек(x) ∧ ∃xЖивотное(x))",
        "∀x∃y(Любит(x,y) ∧ ∀zЗнает(x,z))"  # Новый тест с несколькими кванторами
    ]
    
    for i, formula in enumerate(test_cases, 1):
        print(f"\n\n{'#'*70}")
        print(f"ТЕСТ {i}: {formula}")
        print(f"{'#'*70}")
        
        processor = ResolutionPreprocessor()
        result = processor.parse_formula(formula)
        print("ДО ПРЕОБРАЗОВАНИЙ:")
        processor.print_analysis()
        
        # Полная подготовка к резолюции методом класса
        variable_map = processor.prepare_for_resolution(i)
        
        print(f"\nРезультат подготовки:")
        print(f"Отображение переменных: {variable_map}")