# Импортируем модули
from first import LogicFormalizer
from second import ResolutionEngine
# Если у вас есть third.py с объяснителем:
# from third import ProofExplainer

class LogicalProofSystem:
    def __init__(self):
        self.formalizer = LogicFormalizer()
        self.resolution_engine = ResolutionEngine()
        # self.explainer = ProofExplainer()  # раскомментируйте если есть
        
    def prove_statement(self, natural_language_statement):
        print(f"Вход: {natural_language_statement}")
        
        # Шаг 1: Формализация
        print("\n1. Формализация задачи...")
        formulas = self.formalizer.formalize_problem(natural_language_statement)
        print(f"Исходные формулы: {formulas}")
        
        # Убедимся, что есть отрицание цели
        if not any(f.startswith('¬') for f in formulas) and len(formulas) >= 2:
            # Берем последний предикат и отрицаем его
            last_formula = formulas[-1]
            if '(' in last_formula and not last_formula.startswith('∀'):
                negated_goal = f"¬{last_formula}"
                formulas.append(negated_goal)
                print(f"   Добавлено отрицание цели: {negated_goal}")
        
        # Шаг 2: Доказательство
        print("\n2. Доказательство методом резолюций...")
        success, proof_log = self.resolution_engine.prove_by_resolution(formulas)
        
        print("   Лог доказательства:")
        for step in proof_log:
            print(f"   │ {step}")
        
        print(f"\n3. Результат: {'ДОКАЗАНО' if success else 'НЕ ДОКАЗАНО'}")
        
        return success, formulas, proof_log

def main():
    system = LogicalProofSystem()
    
    print("=" * 60)
    print("СИСТЕМА ЛОГИЧЕСКОГО ДОКАЗАТЕЛЬСТВА")
    print("=" * 60)
    
    while True:
        print("\n" + "─" * 40)
        print("Выберите режим:")
        print("1 - Ввести задачу вручную")
        print("2 - Протестировать примеры")
        print("0 - Выход")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "1":
            user_input = input("\nВведите логическую задачу: ")
            if user_input.lower() in ['выход', 'exit', 'quit']:
                break
            success, formulas, proof_log = system.prove_statement(user_input)
            
        elif choice == "2":
            test_cases = [
                "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.",
                "Все кошки животные. Мурка кошка. Следовательно, Мурка животное.",
                "Если идет дождь, то улица мокрая. Дождь идет. Значит, улица мокрая."
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\nПример {i}: {test_case}")
                success, formulas, proof_log = system.prove_statement(test_case)
                
        elif choice == "0":
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()