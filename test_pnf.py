from parsing import FormulaParser, Predicate, LogicalExpression
from pnf_convert import PNF_Converter, standardize_variables

class TestPNFConverter:
    """Класс для тестирования преобразований в ПНФ"""
    
    def __init__(self):
        self.converter = PNF_Converter()
        self.test_count = 0
        self.passed_count = 0
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("=" * 70)
        print("ТЕСТИРОВАНИЕ ПРЕОБРАЗОВАНИЯ В ПНФ")
        print("=" * 70)
        
        self.test_implication_elimination()
        self.test_negation_handling()
        self.test_quantifier_movement()
        self.test_complex_expressions()  # Новый тест для сложных выражений
        self.test_complete_pnf_transformation()
        self.test_variable_standardization()
        
        print("\n" + "=" * 70)
        print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {self.passed_count}/{self.test_count} пройдено")
        print("=" * 70)
    
    def test_implication_elimination(self):
        """Тест устранения импликаций"""
        print("\nТЕСТ 1: УСТРАНЕНИЕ ИМПЛИКАЦИЙ")
        
        test_cases = [
            ("Человек(x) → Смертен(x)", "¬Человек(x) ∨ Смертен(x)"),
            ("A → B", "¬A ∨ B"),
        ]
        
        for formula, expected_pattern in test_cases:
            self._run_pnf_test(formula, lambda: self.converter.step1_pnf(), expected_pattern)
    
    def test_negation_handling(self):
        """Тест обработки отрицаний"""
        print("\nТЕСТ 2: ОБРАБОТКА ОТРИЦАНИЙ")
        
        test_cases = [
            ("¬∀xЧеловек(x)", "∃x¬Человек(x)"),
            ("¬∃xЧеловек(x)", "∀x¬Человек(x)"),
        ]
        
        for formula, expected_pattern in test_cases:
            self._run_pnf_test(formula, lambda: self.converter.step1_pnf(), expected_pattern)
    
    def test_quantifier_movement(self):
        """Тест выноса кванторов влево"""
        print("\nТЕСТ 3: ВЫНОС КВАНТОРОВ ВЛЕВО")
        
        test_cases = [
            ("∀xЧеловек(x) ∧ ∀xСмертен(x)", "∀x∀x(Человек(x) ∧ Смертен(x))"),
            ("∀x(Человек(x) ∧ ∃yЖивотное(y))", "∀x∃y(Человек(x) ∧ Животное(y))"),
        ]
        
        for formula, expected_pattern in test_cases:
            self._run_pnf_test(formula, lambda: self.converter.move_quantifiers_left(), expected_pattern)
    
    def test_complex_expressions(self):
        """Тест сложных выражений с тремя и более предикатами"""
        print("\nТЕСТ 4: СЛОЖНЫЕ ВЫРАЖЕНИЯ (3+ ПРЕДИКАТА)")
        
        test_cases = [
            # Три предиката с конъюнкцией
            ("A ∧ B ∧ C", "A ∧ B ∧ C"),
            ("∀x(P(x) ∧ Q(x) ∧ R(x))", "∀x(P(x) ∧ Q(x) ∧ R(x))"),
            
            # Три предиката с дизъюнкцией
            ("A ∨ B ∨ C", "A ∨ B ∨ C"),
            ("∃x(P(x) ∨ Q(x) ∨ R(x))", "∃x(P(x) ∨ Q(x) ∨ R(x))"),
            
            # Смешанные операторы
            ("(A ∧ B) ∨ C", "A ∧ B ∨ C"),
            ("A ∧ (B ∨ C)", "A ∧ B ∨ C"),
            ("(A ∨ B) ∧ C", "A ∨ B ∧ C"),
            
            # Цепочка импликаций
            ("A → B → C", "¬A ∨ ¬B ∨ C"),
            ("(A → B) → C", "¬(¬A ∨ B) ∨ C"),
            
            # Множественные кванторы с тремя предикатами
            ("∀x∃y∀z(P(x) ∧ Q(y) ∧ R(z))", "∀x∃y∀z(P(x) ∧ Q(y) ∧ R(z))"),
            ("∀x(P(x) → Q(x) → R(x))", "∀x(¬P(x) ∨ ¬Q(x) ∨ R(x))"),
            
            # Глубоко вложенные выражения
            ("∀x((P(x) ∧ Q(x)) → (R(x) ∨ S(x)))", "∀x(¬(P(x) ∧ Q(x)) ∨ R(x) ∨ S(x))"),
            ("¬∀x∃y(P(x) ∧ Q(y) ∧ R(x,y))", "∃x∀y(¬P(x) ∨ ¬Q(y) ∨ ¬R(x,y))"),
            
            # Четыре предиката
            ("A ∧ B ∧ C ∧ D", "A ∧ B ∧ C ∧ D"),
            ("∀x(P(x) ∧ Q(x) ∧ R(x) ∧ S(x))", "∀x(P(x) ∧ Q(x) ∧ R(x) ∧ S(x))"),
            
            # Комплексные выражения с разными операторами
            ("(A → B) ∧ (C → D)", "(¬A ∨ B) ∧ (¬C ∨ D)"),
            ("∀x(P(x) → Q(x)) ∧ ∃y(R(y) → S(y))", "∀x∃y((¬P(x) ∨ Q(x)) ∧ (¬R(y) ∨ S(y)))"),
        ]
        
        for formula, expected_pattern in test_cases:
            self._run_complex_test(formula, expected_pattern)
    
    def test_complete_pnf_transformation(self):
        """Тест полного преобразования в ПНФ"""
        print("\nТЕСТ 5: ПОЛНОЕ ПРЕОБРАЗОВАНИЕ В ПНФ")
        
        test_cases = [
            ("∀x(Человек(x) → Смертен(x))", "∀x(¬Человек(x) ∨ Смертен(x))"),
            ("¬∀x(Человек(x) → Смертен(x))", "∃x(Человек(x) ∧ ¬Смертен(x))"),
        ]
        
        for formula, expected_pattern in test_cases:
            self._run_complete_pnf_test(formula, expected_pattern)
    
    def test_variable_standardization(self):

        print("\nТЕСТ 6: СТАНДАРТИЗАЦИЯ ПЕРЕМЕННЫХ")
        
        # ДИАГНОСТИКА: посмотрим на структуру выражений перед стандартизацией
        diagnostic_formulas = [
            "∀xЧеловек(x)",
            "∀x∃yЛюбит(x,y)",
            "∀x(P(x) ∧ ∀xQ(x))",
            "∀x∃y∀z(P(x,y) ∧ Q(y,z) ∧ R(x,z))"
        ]
        
        print("\n--- ДИАГНОСТИКА СТРУКТУРЫ ---")
        for i, formula in enumerate(diagnostic_formulas, 1):
            print(f"\nФормула {i}: {formula}")
            self.converter.parse_formula(formula)
            print("Структура после парсинга:")
            self.converter.print_analysis()
            print("Строковое представление:", self.converter.to_string())
            
            # Покажем внутреннюю структуру выражения
            print("Внутренняя структура выражения:")
            self._debug_expression_structure(self.converter.expression, 0)
            
            # Применим ПНФ преобразования
            print("После step1_pnf():")
            self.converter.step1_pnf()
            self.converter.print_analysis()
            
            print("После move_quantifiers_left():")
            self.converter.move_quantifiers_left()
            self.converter.print_analysis()
            
            # Попробуем стандартизацию
            print("После стандартизации переменных:")
            variable_map = standardize_variables(self.converter.expression, i)
            print(f"Отображение переменных: {variable_map}")
            self.converter.print_analysis()
            print("=" * 50)
        
        print("\n--- ЗАПУСК ОСНОВНЫХ ТЕСТОВ ---")
        test_cases = [
            ("∀xЧеловек(x)", "x_1"),
            ("∀x∃yЛюбит(x,y)", ["x_2", "y_2"]),
            ("∀x(P(x) ∧ ∀xQ(x))", "x_3"),
            ("∀x∃y∀z(P(x,y) ∧ Q(y,z) ∧ R(x,z))", ["x_4", "y_4", "z_4"]),
        ]
        
        for formula, expected_vars in test_cases:
            self._run_standardization_test(formula, expected_vars)

    def _debug_expression_structure(self, expr, indent=0):
        """Рекурсивно выводит структуру выражения для отладки"""
        indent_str = "  " * indent
        
        if isinstance(expr, LogicalExpression):
            print(f"{indent_str}LogicalExpression:")
            print(f"{indent_str}  operator: '{expr.operator}'")
            print(f"{indent_str}  expression_negated: {expr.expression_negated}")
            print(f"{indent_str}  quantifiers: {expr.quantifiers}")
            
            if expr.left:
                print(f"{indent_str}  left:")
                self._debug_expression_structure(expr.left, indent + 2)
            else:
                print(f"{indent_str}  left: None")
                
            if expr.right:
                print(f"{indent_str}  right:")
                self._debug_expression_structure(expr.right, indent + 2)
            else:
                print(f"{indent_str}  right: None")
                
        elif isinstance(expr, Predicate):
            print(f"{indent_str}Predicate:")
            print(f"{indent_str}  name: '{expr.name}'")
            print(f"{indent_str}  argument: '{expr.argument}'")
            print(f"{indent_str}  negated: {expr.negated}")
            print(f"{indent_str}  quantifier: '{expr.quantifier}'")
        else:
            print(f"{indent_str}Unknown type: {type(expr)}")
    
    def _run_pnf_test(self, formula, transformation_func, expected_pattern):
        """Запуск одного теста ПНФ"""
        self.test_count += 1
        
        try:
            self.converter.parse_formula(formula)
            transformation_func()
            result_string = self.converter.to_string()
            
            # Проверяем результат
            self._validate_pnf_result(result_string, expected_pattern)
            
            print(f"ТЕСТ {self.test_count}: ✅ ПРОЙДЕН")
            self.passed_count += 1
            
        except Exception as e:
            print(f"ТЕСТ {self.test_count}: ❌ ПРОВАЛЕН - {e}")
    
    def _run_complex_test(self, formula, expected_pattern):
        """Запуск теста сложных выражений"""
        self.test_count += 1
        
        try:
            self.converter.parse_formula(formula)
            self.converter.step1_pnf()
            self.converter.move_quantifiers_left()
            result_string = self.converter.to_string()
            
            # Проверяем результат
            self._validate_pnf_result(result_string, expected_pattern)
            self._check_pnf_properties(self.converter.expression)
            
            print(f"ТЕСТ {self.test_count}: ✅ ПРОЙДЕН")
            self.passed_count += 1
            
        except Exception as e:
            print(f"ТЕСТ {self.test_count}: ❌ ПРОВАЛЕН - {e}")
    
    def _run_complete_pnf_test(self, formula, expected_pattern):
        """Запуск теста полного преобразования в ПНФ"""
        self.test_count += 1
        
        try:
            self.converter.parse_formula(formula)
            self.converter.step1_pnf()
            self.converter.move_quantifiers_left()
            result_string = self.converter.to_string()
            
            # Проверяем результат
            self._validate_pnf_result(result_string, expected_pattern)
            self._check_pnf_properties(self.converter.expression)
            
            print(f"ТЕСТ {self.test_count}: ✅ ПРОЙДЕН")
            self.passed_count += 1
            
        except Exception as e:
            print(f"ТЕСТ {self.test_count}: ❌ ПРОВАЛЕН - {e}")
    
    def _run_standardization_test(self, formula, expected_vars):
        """Запуск теста стандартизации переменных"""
        self.test_count += 1
        
        try:
            self.converter.parse_formula(formula)
            self.converter.step1_pnf()
            self.converter.move_quantifiers_left()
            variable_map = standardize_variables(self.converter.expression, self.test_count)
            
            # Проверяем результат
            self._validate_standardization(variable_map, expected_vars)
            
            print(f"ТЕСТ {self.test_count}: ✅ ПРОЙДЕН")
            self.passed_count += 1
            
        except Exception as e:
            print(f"ТЕСТ {self.test_count}: ❌ ПРОВАЛЕН - {e}")
    
    def _validate_pnf_result(self, result, expected_pattern):
        """Проверка результата ПНФ преобразования"""
        if result == "":
            raise AssertionError("Результат преобразования пустой")
        
        if "→" in result:
            raise AssertionError(f"В результате осталась импликация: {result}")
    
    def _check_pnf_properties(self, expr):
        """Рекурсивная проверка свойств ПНФ"""
        if isinstance(expr, LogicalExpression):
            if expr.operator == '→':
                raise AssertionError("Найдена импликация в ПНФ")
            
            if expr.left:
                self._check_pnf_properties(expr.left)
            if expr.right:
                self._check_pnf_properties(expr.right)
    
    def _validate_standardization(self, variable_map, expected_vars):
        """Проверка результата стандартизации"""
        unique_vars = set(variable_map.values())
        if len(unique_vars) != len(variable_map.values()):
            raise AssertionError("Не все переменные уникальны")
        
        for new_var in variable_map.values():
            if not new_var.startswith(('x_', 'y_', 'z_')):
                raise AssertionError(f"Некорректный формат переменной: {new_var}")
        
        # Проверяем ожидаемое количество переменных
        if isinstance(expected_vars, list):
            if len(variable_map) != len(expected_vars):
                raise AssertionError(f"Ожидалось {len(expected_vars)} переменных, получено {len(variable_map)}")
        else:
            if len(variable_map) != 1:
                raise AssertionError(f"Ожидалась 1 переменная, получено {len(variable_map)}")


if __name__ == "__main__":
    # Запуск всех тестов
    tester = TestPNFConverter()
    tester.run_all_tests()