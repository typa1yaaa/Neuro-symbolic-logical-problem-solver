import re

class ResolutionEngine:
    def __init__(self):
        self.steps_log = []
        self.variable_counter = 0

    def prove_by_resolution(self, formulas):
        """Доказывает утверждение методом резолюций"""
        self.steps_log = []
        self.variable_counter = 0
        try:
            clauses = self.convert_to_ground_clauses(formulas)
            self.steps_log.append(f"Исходные клаузы: {clauses}")
            result = self.resolution_procedure(clauses)
            return result, self.steps_log
        except Exception as e:
            self.steps_log.append(f"Ошибка: {e}")
            return False, self.steps_log

    def convert_to_ground_clauses(self, formulas):
        """Преобразует формулы в бескванторные клаузы с конкретными термами"""
        clauses = []
        constants = self.extract_constants(formulas)

        for formula in formulas:
            if formula.startswith('∀') and '→' in formula:
                ground_clauses = self.process_universal_implication(formula, constants)
                clauses.extend(ground_clauses)
            elif '→' in formula and not formula.startswith('∀'):
                clauses.append(self.process_implication(formula))
            else:
                clauses.append(formula)

        return clauses

    def extract_constants(self, formulas):
        """Извлекает все константы из формул"""
        constants = set()
        for formula in formulas:
            matches = re.findall(r'\(([^),]+)\)', formula)
            for match in matches:
                const = match.strip()
                if len(const) > 1 or not const.islower():
                    constants.add(const)
        return list(constants)

    def process_universal_implication(self, formula, constants):
        """Обрабатывает универсальные импликации - создает ground instances"""
        clauses = []
        start = formula.find('(') + 1
        end = formula.rfind(')')
        inner = formula[start:end]

        if '→' in inner:
            left, right = inner.split('→')
            left_pred = left.strip()
            right_pred = right.strip()

            for const in constants:
                left_ground = left_pred.replace('(x)', f'({const})').replace('x', const)
                right_ground = right_pred.replace('(x)', f'({const})').replace('x', const)
                clause = f"¬{left_ground} ∨ {right_ground}"
                clauses.append(clause)

        return clauses

    def process_implication(self, formula):
        """Обрабатывает обычные импликации"""
        parts = formula.split('→')
        if len(parts) == 2:
            left, right = parts[0].strip(), parts[1].strip()
            return f"¬{left} ∨ {right}"
        return formula

    def resolution_procedure(self, clauses):
        """Основная процедура резолюции FOL"""
        known_clauses = set(self.normalize_clause(c) for c in clauses)
        new_clauses_added = True
        step = 1

        while new_clauses_added:
            new_clauses_added = False
            current_clauses = list(known_clauses)

            for i in range(len(current_clauses)):
                for j in range(i + 1, len(current_clauses)):
                    c1, c2 = current_clauses[i], current_clauses[j]
                    resolvents = self.find_all_resolvents(c1, c2)

                    for r in resolvents:
                        if not r:
                            continue
                        normalized_r = self.normalize_clause(r)

                        if normalized_r == "□":
                            self.steps_log.append(f"Шаг {step}: Резолюция '{c1}' и '{c2}' -> '□'")
                            self.steps_log.append("🎉 Найдено противоречие! Доказательство завершено.")
                            return True

                        if normalized_r not in known_clauses:
                            known_clauses.add(normalized_r)
                            self.steps_log.append(f"Шаг {step}: Резолюция '{c1}' и '{c2}' -> '{normalized_r}'")
                            new_clauses_added = True

                        step += 1

        self.steps_log.append("Не удалось найти новых резольвент")
        return False

    def find_all_resolvents(self, clause1, clause2):
        """Находит все возможные резольвенты для двух клауз"""
        resolvents = []
        literals1 = self.split_literals(clause1)
        literals2 = self.split_literals(clause2)

        for lit1 in literals1:
            for lit2 in literals2:
                if self.are_complementary(lit1, lit2):
                    new_literals = [l for l in literals1 if l != lit1] + [l for l in literals2 if l != lit2]
                    new_literals = list(set(new_literals))
                    resolvents.append(' ∨ '.join(new_literals) if new_literals else "□")

        return resolvents

    def split_literals(self, clause):
        if clause == "□" or clause == "":
            return []
        return [lit.strip() for lit in clause.split(' ∨ ')] if ' ∨ ' in clause else [clause.strip()]

    def normalize_clause(self, clause):
        if clause == "□" or clause == "":
            return "□"
        literals = self.split_literals(clause)
        if not literals:
            return "□"
        literals.sort()
        return ' ∨ '.join(literals)

    def are_complementary(self, lit1, lit2):
        norm1 = lit1.replace(' ', '')
        norm2 = lit2.replace(' ', '')
        pred1, args1 = self.parse_literal(norm1)
        pred2, args2 = self.parse_literal(norm2)

        if pred1 == pred2 and args1 == args2:
            return (norm1.startswith('¬') and not norm2.startswith('¬')) or \
                   (not norm1.startswith('¬') and norm2.startswith('¬'))
        return False

    def parse_literal(self, literal):
        if literal.startswith('¬'):
            predicate_part = literal[1:]
        else:
            predicate_part = literal
        start = predicate_part.find('(')
        if start == -1:
            return predicate_part, ""
        pred_name = predicate_part[:start]
        args = predicate_part[start:]
        return pred_name, args

# Тестовые функции
def test_engine():
    engine = ResolutionEngine()

    # Тест 1: Классический пример Сократа
    print("\n=== ТЕСТ 1: СОКРАТ ===")
    formulas1 = ["Человек(Сократ)", "∀x(Человек(x)→Смертен(x))", "¬Смертен(Сократ)"]
    success1, log1 = engine.prove_by_resolution(formulas1)
    print(f"Результат: {success1}")
    for step in log1:
        print(f"  {step}")

    # Тест 2: Мурка — кошка
    print("\n=== ТЕСТ 2: МУРКА ===")
    formulas2 = ["Кошка(Мурка)", "∀x(Кошка(x)→Животное(x))", "¬Животное(Мурка)"]
    success2, log2 = engine.prove_by_resolution(formulas2)
    print(f"Результат: {success2}")
    for step in log2:
        print(f"  {step}")

    # Тест 3: Дождь и мокрая улица
    print("\n=== ТЕСТ 3: ДОЖДЬ ===")
    formulas3 = ["Дождь(сейчас)", "∀x(Дождь(x)→МокраяУлица(x))", "¬МокраяУлица(сейчас)"]
    success3, log3 = engine.prove_by_resolution(formulas3)
    print(f"Результат: {success3}")
    for step in log3:
        print(f"  {step}")

    # Тест 4: Пингвин — не летает
    print("\n=== ТЕСТ 4: ПИНГВИН ===")
    formulas4 = ["Птица(Пингвин)", "∀x(Птица(x)→Летает(x))", "¬Летает(Пингвин)"]
    success4, log4 = engine.prove_by_resolution(formulas4)
    print(f"Результат: {success4}")
    for step in log4:
        print(f"  {step}")

    # Тест 5: Число 7 — нечетное через делимость на 2
    print("\n=== ТЕСТ 5: ЧИСЛО 7 ===")
    formulas5 = ["¬Четное(7)", "∀x(Четное(x)→ДелитсяНа2(x))", "ДелитсяНа2(7)"]
    success5, log5 = engine.prove_by_resolution(formulas5)
    print(f"Результат: {success5}")
    for step in log5:
        print(f"  {step}")

    # Тест 6: Сложная цепочка логических правил
    print("\n=== ТЕСТ 6: СЛОЖНАЯ ЦЕПОЧКА ===")
    formulas6 = [
        "Учёный(Эйнштейн)", 
        "∀x(Учёный(x)→Математик(x))", 
        "∀x(Математик(x)→Умный(x))", 
        "¬Умный(Эйнштейн)"
    ]
    success6, log6 = engine.prove_by_resolution(formulas6)
    print(f"Результат: {success6}")
    for step in log6:
        print(f"  {step}")

    # Тест 7: Отрицание и универсальный квантор
    print("\n=== ТЕСТ 7: НЕЧЕСТНЫЙ ЧЕЛОВЕК ===")
    formulas7 = [
        "Честный(Джон)", 
        "∀x(Честный(x)→ГоворитПравду(x))", 
        "¬ГоворитПравду(Джон)"
    ]
    success7, log7 = engine.prove_by_resolution(formulas7)
    print(f"Результат: {success7}")
    for step in log7:
        print(f"  {step}")

if __name__ == "__main__":
    test_engine()
