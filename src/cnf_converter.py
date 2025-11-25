from copy import deepcopy
from logic_struct import *

class CNFConverterLocal:
    """
    CNF-конвертер для интеграции с LogicalExpression/Predicate
    """

    def convert(self, expr):
        expr = self.remove_implications(expr)
        expr = self.push_negations(expr)
        expr = self.distribute_or(expr)
        return expr

    # Убираем импликации A → B = ¬A ∨ B
    def remove_implications(self, expr):
        if isinstance(expr, Predicate):
            return expr
        if expr.operator == '→':
            left = self.remove_implications(expr.left)
            right = self.remove_implications(expr.right)
            left_neg = deepcopy(left)
            self.negate_expr(left_neg)
            new_expr = LogicalExpression()
            new_expr.left = left_neg
            new_expr.right = right
            new_expr.operator = '∨'
            return new_expr
        else:
            expr.left = self.remove_implications(expr.left) if expr.left else None
            expr.right = self.remove_implications(expr.right) if expr.right else None
            return expr


    # Распространение отрицаний внутрь (De Morgan)
    def push_negations(self, expr):
        if isinstance(expr, Predicate):
            return expr
        if expr.expression_negated:
            expr.expression_negated = False
            self.negate_expr(expr)
        expr.left = self.push_negations(expr.left) if expr.left else None
        expr.right = self.push_negations(expr.right) if expr.right else None
        return expr

    def negate_expr(self, expr):
        if isinstance(expr, Predicate):
            expr.negated = not expr.negated
        elif isinstance(expr, LogicalExpression):
            if expr.operator == '∧':
                expr.operator = '∨'
            elif expr.operator == '∨':
                expr.operator = '∧'
            if expr.left:
                self.negate_expr(expr.left)
            if expr.right:
                self.negate_expr(expr.right)


    # Раскрытие дизъюнкции над конъюнкцией (дистрибутивность)
    def distribute_or(self, expr):
        if isinstance(expr, Predicate):
            return expr
        expr.left = self.distribute_or(expr.left) if expr.left else None
        expr.right = self.distribute_or(expr.right) if expr.right else None

        if expr.operator == '∨':
            if isinstance(expr.left, LogicalExpression) and expr.left.operator == '∧':
                A = expr.left.left
                B = expr.left.right
                C = expr.right
                new_left = LogicalExpression()
                new_left.left = A
                new_left.right = C
                new_left.operator = '∨'

                new_right = LogicalExpression()
                new_right.left = B
                new_right.right = C
                new_right.operator = '∨'

                expr.left = self.distribute_or(new_left)
                expr.right = self.distribute_or(new_right)
                expr.operator = '∧'
            elif isinstance(expr.right, LogicalExpression) and expr.right.operator == '∧':
                A = expr.left
                B = expr.right.left
                C = expr.right.right
                new_left = LogicalExpression()
                new_left.left = A
                new_left.right = B
                new_left.operator = '∨'

                new_right = LogicalExpression()
                new_right.left = A
                new_right.right = C
                new_right.operator = '∨'

                expr.left = self.distribute_or(new_left)
                expr.right = self.distribute_or(new_right)
                expr.operator = '∧'
        return expr

    def skolemize(self, expr, universal_vars=None, counter=[0]):
        if universal_vars is None:
            universal_vars = []

        if isinstance(expr, Predicate):
            return expr

        # Обрабатываем кванторы
        new_quantifiers = []
        for quant, var in getattr(expr, 'quantifiers', []):
            if quant == '∀':
                universal_vars.append(var)
                new_quantifiers.append((quant, var))
            elif quant == '∃':
                # Создаём функцию или константу
                if universal_vars:
                    fname = f"f{counter[0]}({','.join(universal_vars)})"
                else:
                    fname = f"c{counter[0]}"
                counter[0] += 1
                self.replace_variable(expr, var, fname)
                # Не добавляем квантор ∃ в новый список
            # Иначе оставляем как есть

        expr.quantifiers = new_quantifiers

        # Рекурсивно обходим левую и правую часть
        if expr.left:
            expr.left = self.skolemize(expr.left, universal_vars.copy(), counter)
        if expr.right:
            expr.right = self.skolemize(expr.right, universal_vars.copy(), counter)

        return expr

    def replace_variable(self, expr, var, replacement):
        """Рекурсивно заменяет переменную в предикатах"""
        if isinstance(expr, Predicate):
            if expr.argument == var:
                expr.argument = replacement
        elif isinstance(expr, LogicalExpression):
            if expr.left:
                self.replace_variable(expr.left, var, replacement)
            if expr.right:
                self.replace_variable(expr.right, var, replacement)