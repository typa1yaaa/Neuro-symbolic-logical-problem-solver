import re
from parsing import FormulaParser, Predicate, LogicalExpression

class PNF_Converter:
    """Класс для преобразований после парсинга (ПНФ и т.д.)"""
    
    def __init__(self):
        self.expression = LogicalExpression()
        self.parser = FormulaParser()
    
    def parse_formula(self, formula):
        """Разбирает формулу используя парсер"""
        result = self.parser.parse_formula(formula)
        self.expression = self.parser.expression
        return result
    
    def print_analysis(self):
        return self.parser.print_analysis()
    
    def to_string(self):
        return self.parser.to_string()
    
    def step1_pnf(self):
        """Шаг 1 ПНФ: Устранение импликаций и обработка отрицаний"""
        self._eliminate_implications(self.expression)
        self._handle_negations(self.expression)
    
    def _eliminate_implications(self, expr):
        """Рекурсивно устраняет все импликации"""
        if isinstance(expr, LogicalExpression):
            # Рекурсивно обрабатываем подвыражения сначала
            if expr.left:
                self._eliminate_implications(expr.left)
            if expr.right:
                self._eliminate_implications(expr.right)
            
            # Устраняем импликацию
            if expr.operator == "→":
                expr.operator = "∨"
                
                # Создаем отрицание для левой части
                negated_left = self._create_negation(expr.left)
                expr.left = negated_left
    
    def _create_negation(self, expr):
        """Создает отрицание выражения"""
        if isinstance(expr, Predicate):
            # Для предиката просто инвертируем отрицание
            new_pred = Predicate(expr.name, expr.argument)
            new_pred.negated = not expr.negated
            new_pred.quantifier = expr.quantifier
            return new_pred
        elif isinstance(expr, LogicalExpression):
            # Для логического выражения создаем новое с отрицанием
            new_expr = LogicalExpression()
            new_expr.operator = expr.operator
            new_expr.quantifiers = expr.quantifiers.copy()
            new_expr.expression_negated = not expr.expression_negated
            new_expr.left = expr.left
            new_expr.right = expr.right
            return new_expr
        return expr
    
    def _handle_negations(self, expr):
        """Обрабатывает отрицания, вынося их внутрь"""
        if isinstance(expr, LogicalExpression):
            # Если все выражение отрицается
            if expr.expression_negated:
                expr.expression_negated = False
                
                # Меняем кванторы
                new_quantifiers = []
                for quant_type, variable in expr.quantifiers:
                    new_quantifiers.append((self._change_quantifier(quant_type), variable))
                expr.quantifiers = new_quantifiers
                
                # Меняем оператор
                if expr.operator:
                    expr.operator = self._change_operators(expr.operator)
                
                # Отрицаем подвыражения
                if expr.left:
                    expr.left = self._create_negation(expr.left)
                if expr.right:
                    expr.right = self._create_negation(expr.right)
            
            # Рекурсивно обрабатываем подвыражения
            if expr.left:
                self._handle_negations(expr.left)
            if expr.right:
                self._handle_negations(expr.right)
    
    def _state_negative(self, arg):
        return not arg

    def _change_operators(self, arg):
        return '∧' if arg == '∨' else '∨'

    def _change_quantifier(self, arg):
        return '∃' if arg == '∀' else '∀'

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
                
                return {
                    'quantifiers': all_quantifiers,
                    'expression': expr
                }
                
            elif isinstance(expr, Predicate):
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
            
            current_expr = inner_expr
            for quant_type, var in reversed(quantifiers):
                new_expr = LogicalExpression()
                new_expr.quantifiers = [(quant_type, var)]
                new_expr.left = current_expr
                current_expr = new_expr
            
            return current_expr
        
        result = extract_quantifiers(self.expression)
        self.expression = rebuild_expression(result['quantifiers'], result['expression'])
        return self.expression

def standardize_variables(expression, clause_index):
    """
    Исправленная стандартизация переменных
    """
    variable_map = {}
    
    def standardize_recursive(expr):
        if isinstance(expr, LogicalExpression):
            # Обрабатываем кванторы выражения
            new_quantifiers = []
            for quant_type, old_var in expr.quantifiers:
                if old_var and old_var not in variable_map:
                    # Формат: переменная_clauseIndex
                    new_name = f"{old_var}_{clause_index}"
                    variable_map[old_var] = new_name
                new_quantifiers.append((quant_type, variable_map.get(old_var, old_var)))
            expr.quantifiers = new_quantifiers
            
            # Рекурсивно обрабатываем подвыражения
            if expr.left:
                standardize_recursive(expr.left)
            if expr.right:
                standardize_recursive(expr.right)
                
        elif isinstance(expr, Predicate):
            # Обрабатываем квантор предиката (если переменная в quantifier)
            if expr.quantifier and expr.quantifier not in variable_map:
                new_name = f"{expr.quantifier}_{clause_index}"
                variable_map[expr.quantifier] = new_name
                expr.quantifier = new_name
            
            # Обрабатываем переменные в аргументах
            if expr.argument:
                # Разбиваем аргументы и заменяем переменные
                args = [arg.strip() for arg in expr.argument.split(',')]
                new_args = []
                for arg in args:
                    if arg in variable_map:
                        new_args.append(variable_map[arg])
                    else:
                        # Если это новая переменная, добавляем в map
                        if re.match(r'^[a-z]$', arg):
                            new_name = f"{arg}_{clause_index}"
                            variable_map[arg] = new_name
                            new_args.append(new_name)
                        else:
                            new_args.append(arg)
                expr.argument = ','.join(new_args)
    
    standardize_recursive(expression)
    return variable_map
