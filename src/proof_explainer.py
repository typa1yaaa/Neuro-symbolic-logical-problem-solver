"""
Модуль для преобразования формальных логических доказательств в понятные объяснения на естественном языке.
Использует языковую модель для генерации человеко-читаемых объяснений
шагов доказательства методом резолюций.
"""

import subprocess
import re
import os
from typing import List, Optional, Dict, Any


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

    def explain_proof(self, proof_log: List[Dict], success: bool) -> str:
        """
        Преобразует формальные шаги доказательства в понятное объяснение на естественном языке.
        
        Args:
            proof_log: Полный лог доказательства с детальными шагами
            success: Результат доказательства (True/False)
            
        Returns:
            str: Объяснение доказательства на русском языке в формате связного текста.
        """
        # Валидация входных данных
        if not proof_log:
            return "Ошибка: пустой лог доказательства"

        if not isinstance(proof_log, list):
            return "Ошибка: ожидается список шагов доказательства"

        try:
            # Шаг 1: Подготовка данных для промпта
            proof_data = self._prepare_proof_data(proof_log, success)

            # Шаг 2: Построение промпта для языковой модели
            prompt = self._build_explanation_prompt(proof_data)

            # Шаг 3: Выполнение запроса к модели Ollama
            raw_output = self._execute_ollama_query(prompt)

            # Шаг 4: Очистка и форматирование ответа модели
            cleaned_explanation = self._clean_explanation_output(raw_output)

            return cleaned_explanation

        except subprocess.TimeoutExpired:
            return "Таймаут при выполнении запроса к модели"
        except Exception as e:
            return f"Ошибка при генерации объяснения: {str(e)}"

    def _prepare_proof_data(self, proof_log: List[Dict], success: bool) -> Dict[str, Any]:
        """
        Подготавливает структурированные данные доказательства для промпта.
        
        Args:
            proof_log: Полный лог доказательства
            success: Результат доказательства
            
        Returns:
            Dict: Структурированные данные для объяснения
        """
        # Извлечение ключевой информации из лога
        initial_clauses = self._extract_initial_clauses(proof_log)
        resolution_steps = self._extract_resolution_steps(proof_log)
        contradiction_info = self._extract_contradiction_info(proof_log)
        final_message = self._extract_final_message(proof_log)
        
        proof_data = {
            'success': success,
            'initial_clauses': initial_clauses,
            'key_resolution_steps': resolution_steps[:8],  # Ограничиваем ключевые шаги
            'contradiction_info': contradiction_info,
            'final_message': final_message,
            'total_steps': len(proof_log),
            'proof_structure': self._analyze_proof_structure(proof_log)
        }
        
        # Если лог небольшой (≤100 шагов), добавляем полные данные
        if len(proof_log) <= 100:
            proof_data['full_proof_log'] = proof_log
            proof_data['all_resolution_steps'] = resolution_steps
        
        return proof_data

    def _extract_initial_clauses(self, proof_log: List[Dict]) -> List[Dict]:
        """Извлекает исходные клаузы из лога."""
        initial_clauses = []
        for step in proof_log:
            if step.get('type') == 'initial':
                for clause_info in step.get('clauses', []):
                    initial_clauses.append({
                        'id': clause_info.get('id'),
                        'clause': clause_info.get('clause'),
                        'source': clause_info.get('source', '')
                    })
                break
        return initial_clauses

    def _extract_resolution_steps(self, proof_log: List[Dict]) -> List[Dict]:
        """Извлекает шаги резолюции из лога."""
        resolution_steps = []
        for step in proof_log:
            if step.get('type') == 'resolution_step':
                resolution_steps.append({
                    'step_number': step.get('step'),
                    'clause1_id': step.get('clause1_id'),
                    'clause2_id': step.get('clause2_id'),
                    'clause1': step.get('clause1', ''),
                    'clause2': step.get('clause2', ''),
                    'resolvent': step.get('resolvent', ''),
                    'resolvent_id': step.get('resolvent_id'),
                    'unification': step.get('unification', {}),
                    'parents': step.get('parents', [])
                })
        return resolution_steps

    def _extract_contradiction_info(self, proof_log: List[Dict]) -> Optional[Dict]:
        """Извлекает информацию о найденном противоречии."""
        for step in proof_log:
            if step.get('type') == 'contradiction_found':
                return {
                    'step_number': step.get('step'),
                    'clause_id': step.get('clause_id'),
                    'parents': step.get('parents', []),
                    'message': step.get('message', '')
                }
        return None

    def _extract_final_message(self, proof_log: List[Dict]) -> str:
        """Извлекает финальное сообщение из лога."""
        for step in reversed(proof_log):
            if step.get('type') in ['contradiction_found', 'no_new_clauses', 'timeout', 'error']:
                return step.get('message', '')
        return "Доказательство завершено"

    def _analyze_proof_structure(self, proof_log: List[Dict]) -> Dict[str, Any]:
        """Анализирует структуру доказательства."""
        step_types = {}
        for step in proof_log:
            step_type = step.get('type', 'unknown')
            step_types[step_type] = step_types.get(step_type, 0) + 1
            
        return {
            'total_steps': len(proof_log),
            'step_types': step_types,
            'has_contradiction': any(step.get('type') == 'contradiction_found' for step in proof_log),
            'has_errors': any(step.get('type') == 'error' for step in proof_log)
        }

    def _build_explanation_prompt(self, proof_data: Dict[str, Any]) -> str:
        """
        Строит промпт для языковой модели с инструкциями по генерации объяснения.
        
        Args:
            proof_data: Структурированные данные доказательства
        
        Returns:
            str: Полный промпт для отправки модели
        """
        success_text = "успешно" if proof_data['success'] else "не удалось"
        
        # Формируем текст с шагами доказательства
        proof_steps_text = self._format_proof_steps_for_prompt(proof_data)
        
        prompt = f"""
Ты — опытный учитель логики. Твоя задача — преобразовать формальное логическое доказательство методом резолюций в понятное объяснение на естественном русском языке.

ДАННЫЕ ДОКАЗАТЕЛЬСТВА:
- Результат: доказательство {success_text}
- Исходные клаузы: {self._format_initial_clauses(proof_data['initial_clauses'])}
- Всего шагов: {proof_data['total_steps']}

ШАГИ ДОКАЗАТЕЛЬСТВА:
{proof_steps_text}

ИНСТРУКЦИИ:
1. Объясни доказательство как учитель, объясняющий материал студенту
2. Будь последовательным и ясным
3. Используй естественный, плавный русский язык  
4. Объясни смысл ключевых логических шагов
5. Свяжи шаги в единую историю
6. Подчеркни ключевые моменты и выводы
7. Объясни, почему доказательство {success_text}
8. Если доказательство не удалось, объясни возможные причины
9. Избегай излишней формальности, но сохраняй точность
10. Опирайся ТОЛЬКО на предоставленные логические шаги

Формат вывода: связный текст объяснения на русском языке, 5-8 предложений.

ВАЖНО: Обрати внимание на результат доказательства и объясни, с чем связан успех или неудача.
"""

        return prompt

    def _format_initial_clauses(self, initial_clauses: List[Dict]) -> str:
        """Форматирует исходные клаузы для промпта."""
        if not initial_clauses:
            return "нет информации об исходных условиях"
        
        clauses_text = []
        for clause in initial_clauses:
            clause_str = f"{clause['clause']}"
            clauses_text.append(clause_str)
        
        return "; ".join(clauses_text)

    def _format_proof_steps_for_prompt(self, proof_data: Dict[str, Any]) -> str:
        """Форматирует шаги доказательства для промпта."""
        steps_text = []
        
        # Добавляем ключевые шаги резолюции
        for i, step in enumerate(proof_data['key_resolution_steps'][:6]):  # Ограничиваем для читаемости
            step_text = f"Шаг {step['step_number']}: Резолюция клауз {step['clause1_id']} и {step['clause2_id']}"
            step_text += f" -> {step['resolvent']}"
            if step.get('unification'):
                step_text += f" (унификация: {step['unification']})"
            steps_text.append(step_text)
        
        # Добавляем информацию о противоречии
        if proof_data['contradiction_info']:
            contra = proof_data['contradiction_info']
            steps_text.append(f"НАЙДЕНО ПРОТИВОРЕЧИЕ: {contra['message']} (шаг {contra['step_number']})")
        
        # Добавляем финальное сообщение
        if proof_data['final_message']:
            steps_text.append(f"ФИНАЛЬНЫЙ РЕЗУЛЬТАТ: {proof_data['final_message']}")
        
        return "\n".join(steps_text) if steps_text else "Шаги доказательства не детализированы"

    def _execute_ollama_query(self, prompt: str) -> str:
        """
        Выполняет запрос к модели Ollama и возвращает сырой вывод.
        """
        if os.name == 'nt':
            ollama_path = os.path.join(
                os.environ["LOCALAPPDATA"],
                "Programs", "Ollama", "ollama.exe"
            )

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
            
        if process_result.returncode == 0:
            return process_result.stdout.strip()
        else:
            error_details = f"Код ошибки: {process_result.returncode}, Сообщение: {process_result.stderr}"
            raise RuntimeError(f"Ошибка выполнения модели: {error_details}")

    def _clean_explanation_output(self, raw_output: str) -> str:
        """
        Очищает вывод модели от служебных сообщений и артефактов.
        """
        cleaned_text = re.sub(
            r'Thinking\.\.\..*?\.\.\.done thinking\.', 
            '', 
            raw_output, 
            flags=re.DOTALL
        )

        lines = cleaned_text.strip().split('\n')
        explanation_lines = []

        for line in lines:
            line = line.strip()
            if self._should_skip_line(line):
                continue
            explanation_lines.append(line)

        final_explanation = ' '.join(explanation_lines)

        if not final_explanation or len(final_explanation.strip()) < 10:
            return "Не удалось получить содержательное объяснение доказательства"

        return final_explanation

    def _should_skip_line(self, line: str) -> bool:
        """
        Определяет, следует ли пропустить строку при очистке вывода.
        """
        if not line:
            return True

        if line.startswith('...'):
            return True

        skip_keywords = ['Thinking', 'thinking', 'done thinking']
        if any(keyword in line for keyword in skip_keywords):
            return True

        return False