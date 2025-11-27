"""
Модуль для преобразования формальных логических доказательств в понятные объяснения на естественном языке.
Использует языковую модель для генерации человеко-читаемых объяснений
шагов доказательства методом резолюций.
"""

import subprocess
import re
import os
from typing import List, Optional


class ProofExplainer:
    """
    Класс для генерации объяснений формальных логических доказательств.
    
    Преобразует последовательность шагов доказательства методом резолюций
    в понятное текстовое объяснение на русском языке.
    
    Атрибуты:
        model_name (str): Название модели Ollama для генерации объяснений
    """

    def __init__(self, model_name: str = "deepseek-v3.1:671b-cloud"):
        """
        Инициализация объяснителя доказательств.
        
        Args:
            model_name: Название модели Ollama для использования.
                      По умолчанию "deepseek-v3.1:671b-cloud"
        """
        self.model_name = model_name

    def explain_proof(self, proof_steps: List[str]) -> str:
        """
        Преобразует формальные шаги доказательства в понятное объяснение на естественном языке.
        
        Args:
            proof_steps: Список строк с шагами доказательства методом резолюций.
                        Каждая строка описывает один логический шаг.
            
        Returns:
            str: Объяснение доказательства на русском языке в формате связного текста.
        
        Пример:
            >>> explainer = ProofExplainer()
            >>> steps = [
            ...     "Шаг 1: Унификация {x/Сократ} в ¬Человек(x) ∨ Смертен(x)",
            ...     "Шаг 2: Резолюция с Человек(Сократ) -> Смертен(Сократ)",
            ...     "Шаг 3: Резолюция Смертен(Сократ) и ¬Смертен(Сократ) -> Противоречие"
            ... ]
            >>> explanation = explainer.explain_proof(steps)
            >>> print(explanation)
        """
        # Валидация входных данных
        if not proof_steps:
            return "Ошибка: пустой список шагов доказательства"

        if not isinstance(proof_steps, list):
            return "Ошибка: ожидается список шагов доказательства"

        try:
            # Шаг 1: Подготовка текста шагов для промпта
            steps_text = self._prepare_steps_text(proof_steps)

            # Шаг 2: Построение промпта для языковой модели
            prompt = self._build_explanation_prompt(steps_text)

            # Шаг 3: Выполнение запроса к модели Ollama
            raw_output = self._execute_ollama_query(prompt)

            # Шаг 4: Очистка и форматирование ответа модели
            cleaned_explanation = self._clean_explanation_output(raw_output)

            return cleaned_explanation

        except subprocess.TimeoutExpired:
            return "Таймаут при выполнении запроса к модели"
        except Exception as e:
            return f"Ошибка при генерации объяснения: {str(e)}"

    def _prepare_steps_text(self, proof_steps: List[str]) -> str:
        """
        Подготавливает текст шагов доказательства для включения в промпт.
        
        Args:
            proof_steps: Список строк с шагами доказательства
        
        Returns:
            str: Единая строка с объединенными шагами доказательства
        """
        # Объединение шагов через запятую для читаемости
        return ", ".join(proof_steps)

    def _build_explanation_prompt(self, steps_text: str) -> str:
        """
        Строит промпт для языковой модели с инструкциями по генерации объяснения.
        
        Args:
            steps_text: Текст с шагами доказательства для объяснения
        
        Returns:
            str: Полный промпт для отправки модели
        """
        prompt = f"""
Ты — опытный учитель логики. Твоя задача — преобразовать формальное логическое доказательство, представленное в виде последовательности шагов, в понятное объяснение на естественном русском языке.
Объясняй доказательство как будто ты учитель, объясняющий материал студенту:
- Будь последовательным и ясным
- Используй естественный, плавный русский язык
- Объясняй смысл каждого логического шага
- Связывай шаги в единую историю
- Подчеркивай ключевые моменты и выводы
- Избегай излишней формальности, но сохраняй точность
Формат входных данных: список логических шагов
Формат вывода: связный текст объяснения на русском языке, 3-5 предложений.
Примеры:
Вход: [Шаг 1: Унификация {{x/Сократ}} в ¬Человек(x) ∨ Смертен(x). Шаг 2: Резолюция с Человек(Сократ) -> Смертен(Сократ). Шаг 3: Резолюция Смертен(Сократ) и ¬Смертен(Сократ) -> Противоречие.]
Выход: "Давайте разберем доказательство по шагам. У нас есть общее правило: 'Если кто-то является человеком, то он смертен'. Мы применяем это правило к Сократу, подставляя его вместо переменной 'x'. Поскольку нам также известно, что Сократ — человек, мы приходим к выводу, что Сократ смертен. Но это противоречит нашему исходному предположению, что Сократ не является смертным. Это противоречие доказывает, что наше предположение было ложным, а значит, Сократ действительно смертен."
Теперь объясни следующее доказательство: {steps_text}
        """

        return prompt

    def _execute_ollama_query(self, prompt: str) -> str:
        """
        Выполняет запрос к модели Ollama и возвращает сырой вывод.
        
        Args:
            prompt: Текст промпта для отправки модели
        
        Returns:
            str: Сырой вывод от модели Ollama
        
        Raises:
            subprocess.TimeoutExpired: Если выполнение превышает 120 секунд
            Exception: При других ошибках выполнения подпроцесса
        """
        if os.name == 'nt':
            # Запускаем Ollama
            ollama_path = os.path.join(
                os.environ["LOCALAPPDATA"],
                "Programs", "Ollama", "ollama.exe"
            )

            # Параметры для скрытия консоли
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            kwargs = {
                'startupinfo': startupinfo,
                'creationflags': subprocess.CREATE_NO_WINDOW
            }

            process_result = subprocess.run([
                ollama_path, 
                'run', 
                self.model_name, 
                prompt
            ], 
            capture_output=True, 
            text=True, 
            timeout=120, 
            encoding='utf-8',
            **kwargs
            )
                    
        else:
            # Для Linux/Mac (оригинальная версия)
            process_result = subprocess.run([
                'ollama', 
                'run', 
                self.model_name, 
                prompt
            ], 
            capture_output=True, 
            text=True, 
            timeout=120,
            encoding='utf-8')
            
        # Проверка успешности выполнения команды
        if process_result.returncode == 0:
            return process_result.stdout.strip()
        else:
            error_details = f"Код ошибки: {process_result.returncode}, Сообщение: {process_result.stderr}"
            raise RuntimeError(f"Ошибка выполнения модели: {error_details}")

    def _clean_explanation_output(self, raw_output: str) -> str:
        """
        Очищает вывод модели от служебных сообщений и артефактов.
        
        Args:
            raw_output: Сырой текст вывода от языковой модели
        
        Returns:
            str: Очищенное объяснение доказательства
        """
        # Удаление блоков "Thinking..." (размышления модели)
        cleaned_text = re.sub(
            r'Thinking\.\.\..*?\.\.\.done thinking\.', 
            '', 
            raw_output, 
            flags=re.DOTALL
        )

        # Разделение текста на строки для обработки
        lines = cleaned_text.strip().split('\n')
        explanation_lines = []

        for line in lines:
            line = line.strip()

            # Пропуск пустых строк и служебных сообщений
            if self._should_skip_line(line):
                continue

            explanation_lines.append(line)

        # Объединение оставшихся строк в связный текст
        final_explanation = ' '.join(explanation_lines)

        # Проверка наличия содержательного текста
        if not final_explanation or len(final_explanation.strip()) < 10:
            return "Не удалось получить содержательное объяснение доказательства"

        return final_explanation

    def _should_skip_line(self, line: str) -> bool:
        """
        Определяет, следует ли пропустить строку при очистке вывода.
        
        Args:
            line: Строка текста для проверки
        
        Returns:
            bool: True если строку следует пропустить
        """
        # Пустые строки
        if not line:
            return True

        # Строки с многоточием (служебные сообщения)
        if line.startswith('...'):
            return True

        # Строки, содержащие ключевые слова служебных сообщений
        skip_keywords = ['Thinking', 'thinking', 'done thinking']
        if any(keyword in line for keyword in skip_keywords):
            return True

        return False

