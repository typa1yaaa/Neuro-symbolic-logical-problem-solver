"""
Модуль для формализации текстовых задач в логику предикатов первого порядка.
Использует языковую модель Ollama для преобразования естественно-языковых описаний
в формальные логические выражения, готовые для применения метода резолюций.
"""

import subprocess
import re
import os
from typing import List


class LogicFormalizer:
    """
    Класс для преобразования текстовых задач в формальные логические выражения.
    
    Использует языковую модель для выполнения последовательных преобразований:
    1. Предваренная нормальная форма (ПНФ)
    2. Сколемовская нормальная форма (СНФ) 
    3. Удаление кванторов всеобщности
    4. Конъюнктивная нормальная форма (КНФ)
    5. Разделение на дизъюнкты
    
    Атрибуты:
        model_name (str): Название модели Ollama для использования
    """

    def __init__(self, model_name: str = "deepseek-v3.1:671b-cloud"):
        """
        Инициализация формализатора логики.
        
        Args:
            model_name: Название модели Ollama для использования.
                      По умолчанию "deepseek-v3.1:671b-cloud"
        """
        self.model_name = model_name

    def formalize_problem(self, user_input: str) -> List[str]:
        """
        Основной метод для преобразования текстовой задачи в логические формулы.
        
        Args:
            user_input: Текстовое описание логической задачи на естественном языке
        
        Returns:
            List[str]: Список дизъюнктов в формате логики предикатов
        
        Пример:
            >>> formalizer = LogicFormalizer()
            >>> formulas = formalizer.formalize_problem("Сократ человек. Все люди смертны.")
            >>> print(formulas)
            ['Человек(Сократ)', '¬Человек(x) ∨ Смертен(x)']
        """
        prompt = self._build_prompt(user_input)

        try:
            # Шаг 1: Запуск языковой модели через Ollama
            raw_output = self._run_ollama_model(prompt)

            # Шаг 2: Очистка и извлечение формул из вывода модели
            formulas = self._extract_formulas(raw_output)

            return formulas

        except subprocess.TimeoutExpired:
            return ["Таймаут запроса к модели"]
        except Exception as e:
            return [f"Ошибка выполнения: {str(e)}"]

    def _build_prompt(self, user_input: str) -> str:
        """
        Создает промпт для языковой модели с инструкциями по преобразованию.
        
        Args:
            user_input: Исходная текстовая задача от пользователя
        
        Returns:
            str: Форматированный промпт с инструкциями и примером
        """
        prompt_template = """
        Ты — экспертный ассистент по формальной логике. Твоя задача — преобразовать текстовое описание задачи в набор дизъюнктов логики предикатов, готовых для применения метода резолюций.
        ПРАВИЛА ПРЕОБРАЗОВАНИЯ (выполняй строго по порядку):
        1. ПНФ (Предваренная нормальная форма) - вынеси все кванторы в начало формулы
        2. СНФ (Сколемовская нормальная форма) - устрани кванторы существования с помощью сколемовских функций
        3. Удали все кванторы всеобщности (они подразумеваются)
        4. Преобразуй в КНФ (Конъюнктивную нормальная форма) - конъюнкция дизъюнктов
        5. Разбей на отдельные дизъюнкты (раздели конъюнкции)
        ФОРМАТ ВЫВОДА:
        Выводи ТОЛЬКО готовые дизъюнкты в формате:
        Дизъюнкт1, Дизъюнкт2, Дизъюнкт3, ...
        ПРИМЕРЫ:
        Вход: "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен."
        Выход: Человек(Сократ), ¬Человек(x) ∨ Смертен(x), ¬Смертен(Сократ)
        Вход: "Каждый студент сдал какой-то экзамен. Иван — студент. Докажи, что Иван сдал какой-то экзамен."
        Выход: ¬Студент(x) ∨ СдалЭкзамен(x, f(x)), Студент(Иван), ¬СдалЭкзамен(Иван, y)
        СЛЕДИ ЗА:
        - Используй осмысленные имена предикатов
        - Для сколемовских функций используй имена: f, g, h
        - Не включай в вывод кванторы, комментарии или пояснения
        - Разделяй дизъюнкты запятыми
        Теперь преобразуй следующую задачу: {user_input} 
        """

        return prompt_template.format(user_input=user_input)

    def _run_ollama_model(self, prompt: str) -> str:
        """
        Запускает модель Ollama с заданным промптом и возвращает результат.
        
        Args:
            prompt: Текст промпта для модели
        
        Returns:
            str: Сырой вывод от модели Ollama
        
        Raises:
            subprocess.TimeoutExpired: Если выполнение занимает больше 120 секунд
            Exception: При других ошибках выполнения подпроцесса
        """
        # Определение пути к исполняемому файлу Ollama в Windows
        ollama_executable_path = os.path.join(
            os.environ["LOCALAPPDATA"],
            "Programs", "Ollama", "ollama.exe"
        )

        # Проверка существования файла Ollama
        if not os.path.exists(ollama_executable_path):
            raise FileNotFoundError(f"Ollama не найден по пути: {ollama_executable_path}")

        # Запуск процесса Ollama
        process_result = subprocess.run([
            ollama_executable_path,
            "run",
            self.model_name,
            prompt
        ], 
        capture_output=True, 
        text=True, 
        timeout=120,  # Таймаут 2 минуты
        encoding='utf-8')

        # Проверка успешности выполнения
        if process_result.returncode == 0:
            return process_result.stdout.strip()
        else:
            error_message = f"Ошибка модели (код {process_result.returncode}): {process_result.stderr}"
            raise RuntimeError(error_message)

    def _extract_formulas(self, raw_output: str) -> List[str]:
        """
        Извлекает и очищает логические формулы из вывода модели.
        
        Args:
            raw_output: Сырой текст вывода от языковой модели
        
        Returns:
            List[str]: Список очищенных логических формул
        """
        # Шаг 1: Удаление служебных сообщений модели
        cleaned_output = self._remove_model_artifacts(raw_output)

        # Шаг 2: Поиск строк с формулами
        formula_lines = self._find_formula_lines(cleaned_output)

        # Шаг 3: Извлечение и валидация формул
        formulas = self._parse_formulas(formula_lines)

        return formulas if formulas else ["Не удалось извлечь валидные формулы"]

    def _remove_model_artifacts(self, text: str) -> str:
        """
        Удаляет служебные сообщения и артефакты из вывода модели.
        
        Args:
            text: Исходный текст вывода модели
        
        Returns:
            str: Очищенный текст
        """
        # Удаление сообщений о "размышлении" модели
        cleaned_text = re.sub(
            r'Thinking\.\.\..*?\.\.\.done thinking\.', 
            '', 
            text, 
            flags=re.DOTALL
        )

        # Удаление лишних пробелов и пустых строк
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)  # Удаление пустых строк
        cleaned_text = cleaned_text.strip()

        return cleaned_text

    def _find_formula_lines(self, text: str) -> List[str]:
        """
        Находит строки, содержащие логические формулы.
        
        Args:
            text: Очищенный текст для анализа
        
        Returns:
            List[str]: Список строк, потенциально содержащих формулы
        """
        formula_lines = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Признаки логических формул:
            # - Содержат скобки (предикаты с аргументами)
            # - Содержат логические операторы (∨, ¬)
            # - Не содержат служебных слов
            if (('(' in line and ')' in line) or 
                any(logic_symbol in line for logic_symbol in ['∨', '¬', '∧'])):
                formula_lines.append(line)

        return formula_lines

    def _parse_formulas(self, formula_lines: List[str]) -> List[str]:
        """
        Парсит строки и извлекает из них валидные логические формулы.
        
        Args:
            formula_lines: Список строк, потенциально содержащих формулы
        
        Returns:
            List[str]: Список валидных логических формул
        """
        all_formulas = []

        for line in formula_lines:
            # Разделение строки на отдельные формулы по запятым
            potential_formulas = [f.strip() for f in line.split(",") if f.strip()]

            # Фильтрация и валидация формул
            valid_formulas = [
                formula for formula in potential_formulas 
                if self._is_valid_formula(formula)
            ]

            all_formulas.extend(valid_formulas)

        return all_formulas

    def _is_valid_formula(self, formula: str) -> bool:
        """
        Проверяет, является ли строка валидной логической формулой.
        
        Критерии валидности:
        - Содержит открывающую и закрывающую скобки
        - Имеет осмысленную структуру предиката
        - Не содержит явно нелогических конструкций
        
        Args:
            formula: Строка для проверки
        
        Returns:
            bool: True если строка является валидной формулой
        """
        # Базовые проверки
        if not formula or len(formula) < 3:  # Минимальная формула: "P(a)"
            return False

        # Должна содержать парные скобки для аргументов предиката
        if '(' not in formula or ')' not in formula:
            return False

        # Проверка баланса скобок
        if formula.count('(') != formula.count(')'):
            return False

        # Проверка порядка скобок
        open_bracket_pos = formula.find('(')
        close_bracket_pos = formula.find(')')
        if open_bracket_pos > close_bracket_pos:
            return False

        # Дополнительные проверки для сложных формул
        if '∨' in formula or '¬' in formula:
            # Для дизъюнкций и отрицаний выполняем дополнительные проверки
            return self._validate_complex_formula(formula)

        return True

    def _validate_complex_formula(self, formula: str) -> bool:
        """
        Выполняет дополнительную валидацию для сложных формул с операторами.
        
        Args:
            formula: Сложная формула для проверки
        
        Returns:
            bool: True если формула корректна
        """
        try:
            # Проверка на наличие недопустимых символов
            invalid_chars = ['{', '}', '[', ']', '<', '>', ';', '"', "'"]
            if any(char in formula for char in invalid_chars):
                return False

            # Проверка структуры дизъюнкции (если есть)
            if '∨' in formula:
                parts = formula.split('∨')
                if len(parts) < 2:
                    return False
                # Все части дизъюнкции должны быть валидными литералами
                for part in parts:
                    part = part.strip()
                    if not part or not self._is_valid_literal(part):
                        return False

            return True

        except Exception:
            return False

    def _is_valid_literal(self, literal: str) -> bool:
        """
        Проверяет валидность отдельного литерала (предиката с аргументами).
        
        Args:
            literal: Строка литерала для проверки
        
        Returns:
            bool: True если литерал корректен
        """
        literal = literal.strip()

        # Обработка отрицания
        if literal.startswith('¬'):
            literal = literal[1:].strip()

        # Проверка наличия предиката и аргументов
        if '(' not in literal or not literal.endswith(')'):
            return False

        # Извлечение имени предиката
        predicate_name = literal.split('(')[0].strip()
        if not predicate_name or not predicate_name[0].isalpha():
            return False

        return True


# Пример использования
if __name__ == "__main__":
    # Демонстрация работы формализатора
    formalizer = LogicFormalizer()

    # Тестовые примеры
    test_problems = [
        "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.",
        "Каждый студент сдал какой-то экзамен. Иван — студент. Докажи, что Иван сдал какой-то экзамен.",
        "Все кошки — животные. У некоторых животных есть хвост. Докажи, что у некоторых кошек есть хвост."
    ]

    for i, problem in enumerate(test_problems, 1):
        print(f"Проблема {i}: {problem}")
        formulas = formalizer.formalize_problem(problem)
        print(f"Формулы: {formulas}")
        print("-" * 50)