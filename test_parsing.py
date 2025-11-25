from parsing import FormulaParser, Predicate, LogicalExpression

class TestFormulaParser:
    """Класс для тестирования парсера формул"""
    
    def __init__(self):
        self.parser = FormulaParser()
        self.test_count = 0
        self.passed_count = 0
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("=" * 70)
        print("ТЕСТИРОВАНИЕ ПАРСЕРА ЛОГИЧЕСКИХ ФОРМУЛ")
        print("=" * 70)
        
        self.test_simple_predicates()
        self.test_quantifiers()
        self.test_negations()
        self.test_operators()
        self.test_nested_expressions()
        self.test_complex_formulas()
        
        print("\n" + "=" * 70)
        print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {self.passed_count}/{self.test_count} пройдено")
        print("=" * 70)
    
    def test_simple_predicates(self):
        """Тест простых предикатов"""
        print("\n" + "=" * 50)
        print("ТЕСТ 1: ПРОСТЫЕ ПРЕДИКАТЫ")
        print("=" * 50)
        
        test_cases = [
            "Человек(Сократ)",
            "Смертен(Сократ)",
            "P(x)",
            "Q",
        ]
        
        for formula in test_cases:
            self._run_test(formula, f"Простой предикат: {formula}")
    
    def test_quantifiers(self):
        """Тест кванторов"""
        print("\n" + "=" * 50)
        print("ТЕСТ 2: КВАНТОРЫ")
        print("=" * 50)
        
        test_cases = [
            "∀xЧеловек(x)",
            "∃xЧеловек(x)",
            "∀x(Человек(x))",
            "∃x(Человек(x))",
            "∀x∃yЛюбит(x,y)",
        ]
        
        for formula in test_cases:
            self._run_test(formula, f"Кванторы: {formula}")
    
    def test_negations(self):
        """Тест отрицаний"""
        print("\n" + "=" * 50)
        print("ТЕСТ 3: ОТРИЦАНИЯ")
        print("=" * 50)
        
        test_cases = [
            "¬Человек(Сократ)",
            "¬∀xЧеловек(x)",
            "¬∃xЧеловек(x)",
            "¬(Человек(x) ∧ Смертен(x))",
        ]
        
        for formula in test_cases:
            self._run_test(formula, f"Отрицание: {formula}")
    
    def test_operators(self):
        """Тест логических операторов"""
        print("\n" + "=" * 50)
        print("ТЕСТ 4: ЛОГИЧЕСКИЕ ОПЕРАТОРЫ")
        print("=" * 50)
        
        test_cases = [
            "Человек(x) ∧ Смертен(x)",
            "Человек(x) ∨ Бессмертен(x)",
            "Человек(x) → Смертен(x)",
            "A ∧ B ∨ C",
            "(A ∧ B) ∨ C",
        ]
        
        for formula in test_cases:
            self._run_test(formula, f"Операторы: {formula}")
    
    def test_nested_expressions(self):
        """Тест вложенных выражений"""
        print("\n" + "=" * 50)
        print("ТЕСТ 5: ВЛОЖЕННЫЕ ВЫРАЖЕНИЯ")
        print("=" * 50)
        
        test_cases = [
            "∀x(Человек(x) → Смертен(x))",
            "∃x(Человек(x) ∧ ¬Смертен(x))",
            "∀x∀y(Любит(x,y) → Любит(y,x))",
            "(A ∧ B) → (C ∨ D)",
        ]
        
        for formula in test_cases:
            self._run_test(formula, f"Вложенное выражение: {formula}")
    
    def test_complex_formulas(self):
        """Тест сложных формул"""
        print("\n" + "=" * 50)
        print("ТЕСТ 6: СЛОЖНЫЕ ФОРМУЛЫ")
        print("=" * 50)
        
        test_cases = [
            "∀x(Человек(x) → ∃y(Мать(y,x)))",
            "¬∀x(Человек(x) → Смертен(x))",
            "∀x(Человек(x) ∧ ∃yЖивотное(y))",
            "∀x∃y∀z(P(x,y) ∧ Q(y,z) → R(x,z))",
        ]
        
        for formula in test_cases:
            self._run_test(formula, f"Сложная формула: {formula}")
    
    def _run_test(self, formula, description):
        """Запуск одного теста"""
        self.test_count += 1
        
        try:
            print(f"\n{'─' * 60}")
            print(f"ТЕСТ {self.test_count}: {description}")
            print(f"Формула: {formula}")
            print('─' * 60)
            
            # Парсим формулу
            result = self.parser.parse_formula(formula)
            
            # Выводим анализ
            self.parser.print_analysis()
            
            # Проверяем строковое представление
            parsed_string = self.parser.to_string()
            print(f"\nСтроковое представление: {parsed_string}")
            
            # Проверяем структурированные данные
            print(f"\nСтруктурированные данные:")
            self._print_parsed_data(result)
            
            # Проверяем корректность парсинга
            self._validate_parsing(formula, result, parsed_string)
            
            print("✅ ТЕСТ ПРОЙДЕН")
            self.passed_count += 1
            
        except Exception as e:
            print(f"❌ ТЕСТ ПРОВАЛЕН: {e}")
            import traceback
            traceback.print_exc()
    
    def _print_parsed_data(self, data, indent=0):
        """Рекурсивный вывод структурированных данных"""
        space = "  " * indent
        
        if not data:
            return
        
        if data['type'] == 'expression':
            print(f"{space}ВЫРАЖЕНИЕ:")
            print(f"{space}  Кванторы: {data['quantifiers']}")
            print(f"{space}  Оператор: {data['operator']}")
            print(f"{space}  Отрицание: {data['expression_negated']}")
            
            if data['left']:
                print(f"{space}  Левая часть:")
                self._print_parsed_data(data['left'], indent + 2)
            
            if data['right']:
                print(f"{space}  Правая часть:")
                self._print_parsed_data(data['right'], indent + 2)
                
        elif data['type'] == 'predicate':
            print(f"{space}ПРЕДИКАТ:")
            print(f"{space}  Квантор: {data['quantifier']}")
            print(f"{space}  Имя: {data['name']}")
            print(f"{space}  Аргумент: {data['argument']}")
            print(f"{space}  Отрицание: {data['negated']}")
    
    def _validate_parsing(self, original_formula, parsed_data, parsed_string):
        """Проверка корректности парсинга"""
        print(f"\nПРОВЕРКА КОРРЕКТНОСТИ:")
        
        # Проверяем, что парсинг не вернул None
        assert parsed_data is not None, "Парсинг вернул None"
        
        # Проверяем, что строковое представление не пустое
        assert parsed_string != "", "Строковое представление пустое"
        
        # Проверяем основные свойства
        self._check_data_structure(parsed_data)
        
        print("✅ Корректность проверена")
    
    def _check_data_structure(self, data):
        """Рекурсивная проверка структуры данных"""
        if data['type'] == 'expression':
            # Проверяем, что оператор корректен
            if data['operator']:
                assert data['operator'] in ['→', '∧', '∨', None], f"Некорректный оператор: {data['operator']}"
            
            # Проверяем кванторы
            for quant_type, var in data['quantifiers']:
                assert quant_type in ['∀', '∃'], f"Некорректный квантор: {quant_type}"
                assert len(var) == 1 and var.isalpha(), f"Некорректная переменная: {var}"
            
            # Рекурсивно проверяем подвыражения
            if data['left']:
                self._check_data_structure(data['left'])
            if data['right']:
                self._check_data_structure(data['right'])
                
        elif data['type'] == 'predicate':
            # Проверяем, что имя предиката не пустое
            assert data['name'] is not None and data['name'] != "", "Имя предиката пустое"
            
            # Проверяем квантор предиката
            if data['quantifier']:
                assert data['quantifier'] in ['∀', '∃'], f"Некорректный квантор предиката: {data['quantifier']}"


def run_specific_tests():
    """Запуск конкретных тестов для отладки"""
    parser = FormulaParser()
    
    # Тестовые случаи для отладки
    test_formulas = [
        "∀x(Человек(x) → Смертен(x))",
        "∃x(Человек(x) ∧ ¬Смертен(x))",
        "∀x(Человек(x) ∧ ∃yЖивотное(y))",
    ]
    
    for formula in test_formulas:
        print(f"\n{'='*70}")
        print(f"ОТЛАДОЧНЫЙ ТЕСТ: {formula}")
        print('='*70)
        
        result = parser.parse_formula(formula)
        parser.print_analysis()
        print(f"Строковое представление: {parser.to_string()}")


if __name__ == "__main__":
    # Запуск всех тестов
    tester = TestFormulaParser()
    tester.run_all_tests()
    
    print("\n\n" + "="*70)
    print("ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ ОТЛАДКИ")
    print("="*70)
    run_specific_tests()