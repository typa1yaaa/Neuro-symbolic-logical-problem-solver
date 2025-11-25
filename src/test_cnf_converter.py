from copy import deepcopy
from cnf_converter import CNFConverterLocal
from second_module import LogicalExpression, Predicate

def print_expr(expr, indent=0):
    space = "  " * indent
    if isinstance(expr, Predicate):
        print(f"{space}{'¬' if expr.negated else ''}{expr.name}({expr.argument})")
    elif isinstance(expr, LogicalExpression):
        print(f"{space}Operator: {expr.operator}, Negated: {expr.expression_negated}")
        if expr.left:
            print(f"{space}Left:")
            print_expr(expr.left, indent+1)
        if expr.right:
            print(f"{space}Right:")
            print_expr(expr.right, indent+1)

def cnf_to_array(expr):
    """
    Преобразует LogicalExpression в массив для CNF:
    [[литералы первой клаузы], [литералы второй клаузы], ...]
    """
    if isinstance(expr, Predicate):
        lit_str = f"{'¬' if expr.negated else ''}{expr.name}({expr.argument})"
        return [[lit_str]]

    left_array = cnf_to_array(expr.left) if expr.left else []
    right_array = cnf_to_array(expr.right) if expr.right else []

    if expr.operator == '∧':
        # конъюнкция: объединяем списки клауз
        return left_array + right_array
    elif expr.operator == '∨':
        # дизъюнкция: объединяем литералы внутри каждой клаузы
        result = []
        for l in left_array:
            for r in right_array:
                result.append(l + r)
        return result
    else:
        return left_array + right_array

def test_expression(expr, description):
    print(f"\n=== {description} ===")
    print("Исходное выражение:")
    print_expr(expr)

    cnf_converter = CNFConverterLocal()
    expr_cnf = cnf_converter.convert(deepcopy(expr))

    print("\nПосле преобразования в CNF:")
    print_expr(expr_cnf)

    array_cnf = cnf_to_array(expr_cnf)
    print("\nМассив после CNF:")
    for i, clause in enumerate(array_cnf, 1):
        print(f"C{i}: {clause}")

if __name__ == "__main__":
    x = 'x'

    # 1. Простая импликация
    left = Predicate(name="Человек", argument=x)
    right = Predicate(name="Смертен", argument=x)
    expr1 = LogicalExpression()
    expr1.left = left
    expr1.right = right
    expr1.operator = '→'
    test_expression(expr1, "Простая импликация ∀x(Человек(x) → Смертен(x))")

    # 2. Отрицание предиката
    pred2 = Predicate(name="Человек", argument="Сократ", negated=True)
    test_expression(pred2, "Отрицание предиката ¬Человек(Сократ)")

    # 3. Конъюнкция с отрицанием
    p3a = Predicate(name="A", argument=x)
    p3b = Predicate(name="B", argument=x, negated=True)
    expr3 = LogicalExpression()
    expr3.left = p3a
    expr3.right = p3b
    expr3.operator = '∧'
    expr3.expression_negated = True
    test_expression(expr3, "Отрицание конъюнкции ¬(A ∧ ¬B)")

    # 4. Дизъюнкция над конъюнкцией
    p4a = Predicate(name="P", argument=x)
    p4b = Predicate(name="Q", argument=x)
    p4c = Predicate(name="R", argument=x)
    left4 = LogicalExpression()
    left4.left = p4a
    left4.right = p4b
    left4.operator = '∧'
    expr4 = LogicalExpression()
    expr4.left = left4
    expr4.right = p4c
    expr4.operator = '∨'
    test_expression(expr4, "Дизъюнкция над конъюнкцией (A ∧ B) ∨ C")

    # 5. Сложная формула с несколькими шагами
    p5a = Predicate(name="A", argument=x)
    p5b = Predicate(name="B", argument=x)
    p5c = Predicate(name="C", argument=x)
    imp = LogicalExpression()
    imp.left = p5a
    imp.right = p5b
    imp.operator = '→'
    expr5 = LogicalExpression()
    expr5.left = imp
    expr5.right = p5c
    expr5.operator = '∨'
    test_expression(expr5, "Сложная формула (A → B) ∨ C")
