import subprocess
import re
import os

class LogicFormalizer:
    def __init__(self, model_name="deepseek-v3.1:671b-cloud"):
        self.model_name = model_name
    
    def formalize_problem(self, user_input: str):
        """
        Преобразование текстовую задачу в набор формул логики предикатов
        """
        prompt = f"""
        Ты — экспертный ассистент по формальной логике. Преобразуй следующую текстовую задачу в набор формул логики предикатов. 

        Используй предикаты типа Человек(x), Смертен(x), Говорит_Правду(x). 
        Выведи ТОЛЬКО формулы в формате: Предикат(Объект) или ¬Предикат(Объект), разделяя их запятыми.

        ВАЖНЫЕ ПРАВИЛА:
        1. Используй простые имена предикатов без пробелов: Дождь(x), Мокрая_Улица(x)
        2. Для универсальных утверждений используй формат: ∀x(Предикат(x)→ДругойПредикат(x))
        3. Для экзистенциальных утверждений используй формат: ∃x(Предикат(x)∧ДругойПредикат(x))
        4. Если в задаче нужно что-то ДОКАЗАТЬ, определи что именно доказывается и добавь ОТРИЦАНИЕ этого утверждения
        5. Если в задаче УЖЕ есть отрицание ("не", "ложь", "неверно"), то доказываемое утверждение должно обозначать обратное
        6. Используй одинаковые имена для одинаковых объектов

        Примеры:
        Вход: "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен."
        Выход: ∃xЧеловек(x), ∀x(Человек(x)→Смертен(x)), ¬∃x(Смертен(x))

        Вход: "Все кошки животные. Мурка кошка. Следовательно, Мурка животное."
        Выход: ∀x(Кошка(x)→Животное(x)), ∃x(Кошка(x)), ¬∃x(Животное(x))

        Вход: "Все честные люди говорят правду. Джон лжет. Докажи, что Джон не честный человек."
        Выход: ∀x(Честный(x)→Говорит_Правду(x)), ∃x(¬Говорит_Правду(x)), ∃x(Честный(x))

        Вход: "Если идет дождь, то улица мокрая. Дождь идет. Значит, улица мокрая."
        Выход: ∀x(Дождь(x)→Мокрая_Улица(x)), ∃x(Дождь(x)), ¬∃x(Мокрая_Улица(x))

        Вход: "Некоторые люди богаты. Все богатые люди счастливы. Докажи, что существуют счастливые люди."
        Выход: ∃x(Человек(x)∧Богат(x)), ∀x(Богат(x)→Счастлив(x)), ¬∃x(Счастлив(x))

        Вход: "Существуют умные студенты. Все умные студенты успешны. Докажи, что есть успешные студенты."
        Выход: ∃x(Студент(x)∧Умный(x)), ∀x(Умный(x)→Успешный(x)), ¬∃x(Студент(x)∧Успешный(x))

        Вход: "Каждый любит кого-то. Докажи, что существует тот, кого любят."
        Выход: ∀x∃y(Любит(x,y)), ¬∃y∀x(Любит(x,y))

        Теперь преобразуй следующую задачу: {user_input}
        """
        try:
            # Запускаем Ollama
            ollama_path = os.path.join(
                os.environ["LOCALAPPDATA"],
                "Programs", "Ollama", "ollama.exe"
            )

            result = subprocess.run([
                ollama_path,
                "run",
                self.model_name,
                prompt
            ], capture_output=True, text=True, timeout=120, encoding='utf-8')
            
            if result.returncode == 0:
                raw_output = result.stdout.strip()
                formulas = self.clean_formulas(raw_output)
                return formulas
            else:
                return ["Ошибка выполнения модели"]
                
        except subprocess.TimeoutExpired:
            return ["Таймаут запроса"]
        except Exception as e:
            return [f"Ошибка: {str(e)}"]
    
    def clean_formulas(self, raw_output: str):
        """Очищает вывод и извлекает формулы"""
        # Убираем служебные сообщения
        cleaned = re.sub(r'Thinking\.\.\..*?\.\.\.done thinking\.', '', raw_output, flags=re.DOTALL)
        
        # Ищем формулы (содержат скобки, могут содержать кванторы, отрицания)
        lines = cleaned.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or 'Thinking' in line:
                continue
            
            # Ищем последовательности формул, разделенных запятыми
            if any(char in line for char in ['(', ')', '∀', '∃', '¬', '→']):
                # Разделяем по запятым и очищаем
                formulas = [f.strip() for f in line.split(",") if f.strip()]
                # Фильтруем только валидные формулы
                valid_formulas = []
                for formula in formulas:
                    if self.is_valid_formula(formula):
                        valid_formulas.append(formula)
                if valid_formulas:
                    return valid_formulas
        
        return ["Не удалось извлечь формулы"]
    
    def is_valid_formula(self, formula: str) -> bool:
        """Проверяет, является ли строка валидной формулой"""
        # Должна содержать скобки или быть квантором
        if '(' in formula and ')' in formula:
            return True
        if formula.startswith('∀') or formula.startswith('∃'):
            return True
        return False

# Тестирование формализатора с отрицаниями
def test_formalizer_with_negations():
    formalizer = LogicFormalizer()
    
    test_cases = [
        # Классические задачи
        "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.",
        
        # Задачи с отрицаниями в посылках
        "Все честные люди говорят правду. Джон лжет. Докажи, что Джон не честный человек.",
        "Все млекопитающие теплокровные. Змея не теплокровная. Следовательно, змея не млекопитающее.",
        
        # Задачи с отрицаниями в цели
        "Все рыбы живут в воде. Кит не рыба. Докажи, что кит не обязательно живет в воде.",
        "Все птицы летают. Пингвин не летает. Значит, пингвин не птица.",
        
        # Смешанные случаи
        "Если число четное, то оно делится на 2. Число 7 не делится на 2. Докажи, что число 7 не четное."
    ]
    
    print("ТЕСТИРОВАНИЕ ФОРМАЛИЗАЦИИ С ОТРИЦАНИЯМИ")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nТест {i}: {test_case}")
        result = formalizer.formalize_problem(test_case)
        print(f"Формулы: {result}")
        
        # Анализируем результат
        has_negation = any('¬' in f for f in result)
        print(f"Содержит отрицание: {has_negation}")
        
        if has_negation:
            negated_formulas = [f for f in result if '¬' in f]
            print(f"Отрицательные формулы: {negated_formulas}")

if __name__ == "__main__":
    test_formalizer_with_negations()