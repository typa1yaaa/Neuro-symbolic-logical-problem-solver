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

class ResolutionPreprocessor:
    def __init__(self):
        self.expression = LogicalExpression()
    
    def parse_formula(self, formula):
        """Разбирает формулу на составляющие"""
        self.expression = LogicalExpression()
        return self._parse_recursive(formula.strip())
    
    def _parse_recursive(self, formula):
        """Рекурсивно разбирает формулу"""
        current_expr = LogicalExpression()
        remaining = formula.strip()
        
        # Шаг 1: Проверяем отрицание всего выражения
        if remaining.startswith('¬'):
            current_expr.expression_negated = True
            remaining = remaining[1:].strip()
            current_expr.steps_log.append("Общее отрицание выражения: ДА")
        
        # Шаг 2: Извлекаем кванторы из начала (это кванторы ВСЕГО выражения)
        while remaining.startswith(('∀', '∃')):
            match = re.match(r'([∀∃])([a-z])', remaining)
            if match:
                quant_type = match.group(1)
                variable = match.group(2)
                
                # Проверяем следующий символ после квантора
                next_char_index = 2  # после ∀x или ∃x
                
                if next_char_index < len(remaining) and remaining[next_char_index] == '(':
                    # Квантор ВСЕГО выражения: ∃x(...)
                    content_start = next_char_index
                    
                    # Находим закрывающую скобку
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
                    current_expr.steps_log.append(f"Добавлен квантор ВЫРАЖЕНИЯ: {quant_type}{variable}")
                    
                else:
                    # Квантор предиката: ∃xЧеловек(x) - обрабатываем в _parse_predicate
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
            
            # Рекурсивно разбираем левую и правую части
            current_expr.left = self._parse_side(left_part.strip())
            current_expr.right = self._parse_side(right_part.strip())
            
            current_expr.steps_log.append(f"Найден оператор: {found_operator}")
        else:
            # Одиночный предикат
            current_expr.left = self._parse_side(remaining.strip())
            current_expr.steps_log.append("Оператор: отсутствует")
        
        self.expression = current_expr
        return self.get_parsed_data()
    
    def _parse_side(self, expression):
        """Разбирает левую или правую часть выражения"""
        expression = expression.strip()
        
        # Убираем внешние скобки
        if expression.startswith('(') and expression.endswith(')'):
            expression = expression[1:-1].strip()
        
        # Проверяем, является ли это сложным выражением
        if any(op in expression for op in ['→', '∧', '∨']):
            # Рекурсивно разбираем как выражение
            return self._parse_recursive(expression)
        else:
            # Это предикат (может содержать квантор предиката)
            return self._parse_predicate(expression)
    
    def _parse_predicate(self, expression):
        """Разбирает одиночный предикат (может содержать квантор предиката)"""
        predicate = Predicate()
        expr = expression.strip()
        
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
        match = re.match(r'([^(]+)\(([^)]+)\)', expr)
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

    def step1_pnf(self):
        """Шаг 1 ПНФ: Устранение импликаций и обработка отрицаний"""
        if self.expression.operator == "→":
            self.expression.operator = "∨"
            
            # Инвертируем отрицание левой части
            if isinstance(self.expression.left, Predicate):
                self.expression.left.negated = self._state_negative(self.expression.left.negated)
            elif isinstance(self.expression.left, LogicalExpression):
                self.expression.left.expression_negated = self._state_negative(self.expression.left.expression_negated)

        # Обработка отрицания всего выражения
        if self.expression.expression_negated:
            self.expression.expression_negated = False
            
            # Меняем оператор если он есть
            if self.expression.operator:
                self.expression.operator = self._change_operators(self.expression.operator)
                print("оператор изменен на ", self.expression.operator)
            
            # Меняем кванторы ВЫРАЖЕНИЯ
            new_quantifiers = []
            for quant_type, variable in self.expression.quantifiers:
                new_quantifiers.append((self._change_quantifier(quant_type), variable))
            self.expression.quantifiers = new_quantifiers
            
            # Инвертируем левую и правую части отдельно
            if self.expression.left:
                self._invert_expression_parts_without_negation(self.expression.left)
            if self.expression.right:
                self._invert_expression_parts_without_negation(self.expression.right)

    def _invert_expression_parts_without_negation(self, expr):
        """Рекурсивно инвертирует операторы и отрицания предикатов в выражении"""
        if isinstance(expr, Predicate):
            expr.negated = self._state_negative(expr.negated)
        elif isinstance(expr, LogicalExpression):
            # Инвертируем оператор
            if expr.operator:
                expr.operator = self._change_operators(expr.operator)
            
            # Рекурсивно инвертируем левую и правую части
            if expr.left:
                self._invert_expression_parts_without_negation(expr.left)
            if expr.right:
                self._invert_expression_parts_without_negation(expr.right)
                
    def _state_negative(self, arg):
        """Инвертирует значение отрицания"""
        return not arg

    def _change_operators(self, arg):
        """Меняет операторы: ∧ ↔ ∨"""
        return '∧' if arg == '∨' else '∨'

    def _change_quantifier(self, arg):
        """Меняет кванторы: ∀ ↔ ∃"""
        return '∃' if arg == '∀' else '∀'

    def move_quantifiers_left(self):
        """
        Выносит кванторы влево, сохраняя их последовательность
        """
        def extract_quantifiers(expr):
            if isinstance(expr, LogicalExpression):
                # Собираем кванторы текущего уровня
                quantifiers = expr.quantifiers.copy()
                expr.quantifiers = []
                
                # Рекурсивно извлекаем кванторы из подвыражений
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
                
                # Объединяем все кванторы
                all_quantifiers = quantifiers + left_quantifiers + right_quantifiers
                
                return {
                    'quantifiers': all_quantifiers,
                    'expression': expr
                }
                
            elif isinstance(expr, Predicate):
                # Извлекаем кванторы предикатов
                quantifiers = []
                if expr.quantifier:
                    quantifiers.append((expr.quantifier, expr.argument))
                    expr.quantifier = None
                
                return {
                    'quantifiers': quantifiers,
                    'expression': expr
                }
            
            return {'quantifiers': [], 'expression': expr}
        
        def rebuild_expression(quantifiers, inner_expr):
            if not quantifiers:
                return inner_expr
            
            # Строим цепочку выражений с кванторами
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

    def to_string(self):
        """Преобразует всё выражение в строковое представление"""
        return self.expression.to_string() if self.expression else ""

# Функция prepare_for_resolution остается внешней
def prepare_for_resolution(processor, clause_index):
    """
    Подготовка к резолюции: ПНФ + вынос кванторов + стандартизация переменных
    clause_index - номер клоза для именования переменных
    """
    print("\n" + "="*60)
    print("ПОДГОТОВКА К РЕЗОЛЮЦИИ")
    print("="*60)
    
    # Шаг 1: Преобразование в ПНФ (устранение импликаций и отрицаний)
    print("\n1. ПРЕОБРАЗОВАНИЕ В ПНФ:")
    processor.step1_pnf()
    processor.print_analysis()
    
    # Шаг 2: Вынос всех кванторов влево
    print("\n2. ВЫНОС КВАНТОРОВ ВЛЕВО:")
    processor.move_quantifiers_left()
    processor.print_analysis()
    
    # Шаг 3: Стандартизация переменных
    print("\n3. СТАНДАРТИЗАЦИЯ ПЕРЕМЕННЫХ:")
    variable_map = standardize_variables(processor.expression, clause_index)
    processor.print_analysis()
    
    return variable_map

def standardize_variables(expression, clause_index):
    """
    Стандартизация переменных: делает все имена переменных уникальными
    clause_index - номер клоза для создания уникальных имен
    Возвращает словарь отображения старых имен в новые
    """
    variable_counter = 1
    variable_map = {}  # старое_имя -> новое_уникальное_имя
    
    def standardize_recursive(expr, quantifier_scope=None):
        nonlocal variable_counter
        if quantifier_scope is None:
            quantifier_scope = set()
        
        if isinstance(expr, LogicalExpression):
            # Обрабатываем кванторы выражения
            new_quantifiers = []
            for quant_type, old_var in expr.quantifiers:
                # Создаем новую переменную с учетом номера клоза
                new_var = f"x_{clause_index}_{variable_counter}"
                variable_counter += 1
                variable_map[old_var] = new_var
                new_quantifiers.append((quant_type, new_var))
                quantifier_scope.add(new_var)
            expr.quantifiers = new_quantifiers
            
            # Рекурсивно обрабатываем левую и правую части
            if expr.left:
                standardize_recursive(expr.left, quantifier_scope.copy())
            if expr.right:
                standardize_recursive(expr.right, quantifier_scope.copy())
                
        elif isinstance(expr, Predicate):
            # Обрабатываем квантор предиката
            if expr.quantifier and expr.argument:
                old_var = expr.argument
                if re.match(r'^[a-z]$', old_var):  # если это переменная
                    new_var = f"x_{clause_index}_{variable_counter}"
                    variable_counter += 1
                    variable_map[old_var] = new_var
                    expr.argument = new_var
                    quantifier_scope.add(new_var)
            
            # Заменяем переменные в аргументах предиката
            if expr.argument:
                args = [arg.strip() for arg in expr.argument.split(',')]
                new_args = []
                for arg in args:
                    if re.match(r'^[a-z]$', arg) and arg in variable_map:
                        new_args.append(variable_map[arg])
                    else:
                        new_args.append(arg)
                expr.argument = ','.join(new_args)
    
    # Запускаем стандартизацию
    print("Запуск стандартизации переменных...")
    standardize_recursive(expression)
    print(f"Создано отображение переменных: {variable_map}")
    return variable_map

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
    ]
    
    for i, formula in enumerate(test_cases, 1):
        print(f"\n\n{'#'*70}")
        print(f"ТЕСТ {i}: {formula}")
        print(f"{'#'*70}")
        
        processor = ResolutionPreprocessor()
        result = processor.parse_formula(formula)
        print("ДО ПРЕОБРАЗОВАНИЙ:")
        processor.print_analysis()
        print(f"Строковое представление: {processor.to_string()}")
        
        # Полная подготовка к резолюции с передачей номера клоза
        variable_map = prepare_for_resolution(processor, i)
        
        print(f"\nРезультат стандартизации:")
        print(f"Отображение переменных: {variable_map}")
        print(f"Финальное строковое представление: {processor.to_string()}")