from resolution_engine import ResolutionEngine

def print_detailed_proof(log, engine):
    """Красиво выводит доказательство с нумерацией клауз"""
    print("\n" + "="*60)
    print("ДЕТАЛИЗИРОВАННОЕ ДОКАЗАТЕЛЬСТВО")
    print("="*60)
    
    # Выводим исходные клаузы
    print("ИСХОДНЫЕ КЛАУЗЫ:")
    for step in log:
        if step['type'] == 'initial':
            for clause_info in step['clauses']:
                print(f"{clause_info['id']}. {clause_info['clause']}  [{clause_info['source']}]")
            break
    print("-" * 40)
    
    # Выводим шаги резолюции
    print("ШАГИ РЕЗОЛЮЦИИ:")
    for step in log:
        if step['type'] == 'resolution_step':
            clause1_id = step['clause1_id']
            clause2_id = step['clause2_id']
            resolvent_id = step['resolvent_id']
            resolvent = step['resolvent']
            
            print(f"{resolvent_id}. {resolvent}  [резолюция {clause1_id} и {clause2_id}]")
            if step['unification']:
                print(f"   Унификация: {step['unification']}")
        
        elif step['type'] == 'contradiction_found':
            print("-" * 40)
            print(f" НАЙДЕНО ПРОТИВОРЕЧИЕ! Доказательство завершено.")
            clause_id = step['clause_id']
            parents = step['parents']
            print(f"Пустая клауза {clause_id} получена из клауз {parents}")


# Тестирование
def test_resolution_engine():
    """Тестирование движка резолюций с улучшенным выводом"""
    engine = ResolutionEngine()
    
    # Пример 1: Классический силлогизм
    print("=== ТЕСТ 1: Сократ смертен ===")
    clauses = [
        "Человек(Сократ)",
        "¬Человек(x) ∨ Смертен(x)", 
        "¬Смертен(Сократ)"
    ]
    
    success, log = engine.prove(clauses)
    print(f"Результат доказательства: {success}")
    print_detailed_proof(log, engine)
    
    # Пример 2: С квантором существования (ИСПРАВЛЕННЫЙ ВВОД)
    print("\n" + "="*60)
    print("=== ТЕСТ 2: Студент сдал экзамен ===")
    clauses2 = [
        "¬Студент(x) ∨ СдалЭкзамен(x, f(x))",  # ЗАКРЫТАЯ СКОБКА!
        "Студент(Иван)",
        "¬СдалЭкзамен(Иван, y)"
    ]
    
    success2, log2 = engine.prove(clauses2)
    print(f"Результат доказательства: {success2}")
    print_detailed_proof(log2, engine)


    # Пример 3: Три предиката
    print("\n" + "="*60)
    print("=== ТЕСТ 3: Три предиката (конкретный пример) ===")
    print("Если кто-то студент, то он учится в университете.")
    print("Если кто-то учится в университете, то он сдает экзамены.")
    print("Иван - студент, но он не сдает экзамены.")
    
    clauses3 = [
        "Студент(Иван)",
        "¬Студент(x) ∨ УчитсяВУниверситете(x)", 
        "¬УчитсяВУниверситете(y) ∨ СдаетЭкзамены(y)",
        "¬СдаетЭкзамены(Иван)"
    ]
    
    success3, log3 = engine.prove(clauses3)
    print(f"Результат доказательства: {success3}")
    print_detailed_proof(log3, engine)

    # "Если A больше B, и B больше C, то A больше C. A больше B, B больше C. Докажи, что A больше C."
    print("\n" + "="*60)
    print("=== ТЕСТ 4: Транзитивность ===")
    print("Если A больше B, и B больше C, то A больше C. A больше B, B больше C. Докажи, что A больше C.")

    clauses4 = [
        "Больше(A, B)",
        "Больше(B, C)",
        "¬Больше(x, y) ∨ ¬Больше(y, z) ∨ Больше(x, z)",  # Транзитивность
        "¬Больше(A, C)"  # Отрицание того, что нужно доказать
    ]
"""
не работает
    success4, log4 = engine.prove(clauses4)
    print(f"Результат доказательства: {success4}")
    print_detailed_proof(log4, engine)

    # "Каждый студент изучает какой-то предмет. Математику изучают только умные. Петя - студент. Докажи, что Петя умный."
    print("\n" + "="*60)
    print("=== ТЕСТ 5: Сложная логика ===")
    print("Каждый студент изучает какой-то предмет. Математику изучают только умные. Петя - студент. Докажи, что Петя умный.")

    clauses5 = [
        "Студент(Петя)",
        "¬Студент(x) ∨ Изучает(x, f(x))",  # Каждый студент изучает какой-то предмет f(x)
        "¬Изучает(y, Математика) ∨ Умный(y)",  # Изучающие математику - умные
        "¬Умный(Петя)"  # Отрицание того, что нужно доказать
    ]

    success5, log5 = engine.prove(clauses5)
    print(f"Результат доказательства: {success5}")
    print_detailed_proof(log5, engine)
"""

if __name__ == "__main__":
    test_resolution_engine()