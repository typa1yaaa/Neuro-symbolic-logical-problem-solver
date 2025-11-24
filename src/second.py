class ResolutionEngine:
    def __init__(self):
        self.steps_log = []
        self.variable_counter = 0
    
    def prove_by_resolution(self, formulas):
        """
        Доказывает утверждение методом резолюций
        """
        self.steps_log = []
        self.variable_counter = 0
        
        try:
            # Преобразуем формулы в клаузы (убираем кванторы)
            clauses = self.convert_to_ground_clauses(formulas)
            self.steps_log.append(f"Исходные клаузы: {clauses}")
            
            # Пытаемся найти противоречие
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
                # Универсальная импликация: ∀x(P(x)→Q(x)) 
                ground_clauses = self.process_universal_implication(formula, constants)
                clauses.extend(ground_clauses)
            elif '→' in formula and not formula.startswith('∀'):
                # Обычная импликация: A → B -> ¬A ∨ B
                clause = self.process_implication(formula)
                clauses.append(clause)
            else:
                # Простые предикаты
                clauses.append(formula)
        
        return clauses
    
    def extract_constants(self, formulas):
        """Извлекает все константы из формул"""
        constants = set()
        for formula in formulas:
            # Ищем паттерн Предикат(Константа)
            import re
            matches = re.findall(r'\(([^),]+)\)', formula)
            for match in matches:
                const = match.strip()
                # Считаем константой если не переменная (не одна буква в нижнем регистре)
                if len(const) > 1 or not const.islower():
                    constants.add(const)
        return list(constants)
    
    def process_universal_implication(self, formula, constants):
        """Обрабатывает универсальные импликации - создает ground instances"""
        clauses = []
        
        # Извлекаем предикаты: ∀x(Человек(x)→Смертен(x))
        start = formula.find('(') + 1
        end = formula.rfind(')')
        inner = formula[start:end]
        
        if '→' in inner:
            left, right = inner.split('→')
            left_pred = left.strip()  # Человек(x)
            right_pred = right.strip()  # Смертен(x)
            
            # Создаем ground instances для каждой константы
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
        """Основная процедура резолюции"""
        new_clauses = clauses.copy()
        step = 1
        
        while True:
            if step > 100:
                self.steps_log.append("Превышено максимальное количество шагов")
                return False
            
            found_resolution = False
            current_clauses = new_clauses.copy()
            
            for i in range(len(current_clauses)):
                for j in range(i + 1, len(current_clauses)):
                    clause1, clause2 = current_clauses[i], current_clauses[j]
                    
                    resolvents = self.find_all_resolvents(clause1, clause2)
                    
                    for resolvent in resolvents:
                        if resolvent is None or resolvent == "":
                            continue
                            
                        normalized_resolvent = self.normalize_clause(resolvent)
                        
                        # ПРОВЕРЯЕМ НА ПУСТУЮ КЛАУЗУ СРАЗУ
                        if normalized_resolvent == "" or normalized_resolvent == "□":
                            self.steps_log.append(f"Шаг {step}: Резолюция '{clause1}' и '{clause2}' -> '□'")
                            self.steps_log.append("🎉 Найдено противоречие! Доказательство завершено.")
                            return True
                        
                        self.steps_log.append(f"Шаг {step}: Резолюция '{clause1}' и '{clause2}' -> '{normalized_resolvent}'")
                        
                        if normalized_resolvent not in new_clauses:
                            new_clauses.append(normalized_resolvent)
                            found_resolution = True
                            step += 1
                            break
                    
                    if found_resolution:
                        break
                if found_resolution:
                    break
            
            if not found_resolution:
                self.steps_log.append("Не удалось найти новых резольвент")
                return False
    
    def find_all_resolvents(self, clause1, clause2):
        """Находит все возможные резольвенты для двух клауз"""
        resolvents = []
        
        # Разбиваем на литералы
        literals1 = self.split_literals(clause1)
        literals2 = self.split_literals(clause2)
        
        for lit1 in literals1:
            for lit2 in literals2:
                if self.are_complementary(lit1, lit2):
                    # Создаем резольвенту
                    new_literals = []
                    
                    # Добавляем все литералы кроме complementary пары
                    for l in literals1:
                        if l != lit1:
                            new_literals.append(l)
                    for l in literals2:
                        if l != lit2:
                            new_literals.append(l)
                    
                    # Убираем дубликаты
                    new_literals = list(set(new_literals))
                    
                    if not new_literals:
                        return ["□"]  # Сразу возвращаем пустую клаузу
                    else:
                        resolvent = ' ∨ '.join(new_literals)
                        resolvents.append(resolvent)
        
        return resolvents
    
    def split_literals(self, clause):
        """Разбивает клаузу на литералы"""
        if clause == "□" or clause == "":
            return []
        if ' ∨ ' in clause:
            return [lit.strip() for lit in clause.split(' ∨ ')]
        else:
            return [clause.strip()]
    
    def normalize_clause(self, clause):
        """Нормализует клаузу для сравнения"""
        if clause == "□" or clause == "":
            return "□"
        
        literals = self.split_literals(clause)
        if not literals:
            return "□"
        
        literals.sort()
        return ' ∨ '.join(literals)
    
    def are_complementary(self, lit1, lit2):
        """Проверяет, являются ли литералы complementary"""
        # Нормализуем имена (убираем пробелы)
        norm1 = lit1.replace(' ', '')
        norm2 = lit2.replace(' ', '')
        
        # Извлекаем имена предикатов и аргументы
        pred1, args1 = self.parse_literal(norm1)
        pred2, args2 = self.parse_literal(norm2)
        
        # Проверяем complementary (одинаковые предикаты с одинаковыми аргументами)
        if pred1 == pred2 and args1 == args2:
            if norm1.startswith('¬') and not norm2.startswith('¬'):
                return True
            elif not norm1.startswith('¬') and norm2.startswith('¬'):
                return True
        
        return False
    
    def parse_literal(self, literal):
        """Разбирает литерал на предикат и аргументы"""
        if literal.startswith('¬'):
            predicate_part = literal[1:]
        else:
            predicate_part = literal
        
        # Извлекаем имя предиката и аргументы
        start = predicate_part.find('(')
        if start == -1:
            return predicate_part, ""
        
        pred_name = predicate_part[:start]
        args = predicate_part[start:]
        return pred_name, args

# Тестовые функции
def test_engine():
    engine = ResolutionEngine()
    
    print("=== ТЕСТ 1: СОКРАТ ===")
    formulas1 = ["Человек(Сократ)", "∀x(Человек(x)→Смертен(x))", "¬Смертен(Сократ)"]
    success1, log1 = engine.prove_by_resolution(formulas1)
    print(f"Результат: {success1}")
    for step in log1:
        print(f"  {step}")
    
    print("\n=== ТЕСТ 2: МУРКА ===")
    formulas2 = ["Кошка(Мурка)", "∀x(Кошка(x)→Животное(x))", "¬Животное(Мурка)"]
    success2, log2 = engine.prove_by_resolution(formulas2)
    print(f"Результат: {success2}")
    for step in log2:
        print(f"  {step}")
    
    print("\n=== ТЕСТ 3: ДОЖДЬ ===")
    formulas3 = ["Дождь(сейчас)", "∀x(Дождь(x)→МокраяУлица(x))", "¬МокраяУлица(сейчас)"]
    success3, log3 = engine.prove_by_resolution(formulas3)
    print(f"Результат: {success3}")
    for step in log3:
        print(f"  {step}")

if __name__ == "__main__":
    test_engine()