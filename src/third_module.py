import subprocess
import re

class ProofExplainer:
    def __init__(self, model_name="deepseek-v3.1:671b-cloud"):
        self.model_name = model_name
    
    def explain_proof(self, proof_steps: list) -> str:
        """
        Преобразует формальные шаги доказательства в понятное объяснение на естественном языке
        
        Args:
            proof_steps: Список строк с шагами доказательства
            
        Returns:
            Строка с объяснением на русском языке
        """
        if not proof_steps:
            return "Ошибка: пустой список шагов доказательства"
        
        # Формируем строку с шагами доказательства
        steps_text = ", ".join(proof_steps) if isinstance(proof_steps, list) else str(proof_steps)
        
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
        
        try:
            # Запускаем Ollama
            result = subprocess.run([
                'ollama', 'run', self.model_name, prompt
            ], capture_output=True, text=True, timeout=120, encoding='utf-8')
            
            if result.returncode == 0:
                raw_output = result.stdout.strip()
                # Очищаем вывод от служебных сообщений
                cleaned_output = self.clean_explanation(raw_output)
                return cleaned_output if cleaned_output else "Не удалось получить объяснение"
            else:
                return f"Ошибка выполнения модели: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Таймаут при выполнении запроса"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def clean_explanation(self, raw_output: str) -> str:
        """Очищает вывод модели от служебных сообщений"""
        # Убираем блоки Thinking... и ...done thinking
        cleaned = re.sub(r'Thinking\.\.\..*?\.\.\.done thinking\.', '', raw_output, flags=re.DOTALL)
        
        # Ищем начало объяснения (обычно начинается с ключевых слов)
        lines = cleaned.strip().split('\n')
        explanation_lines = []
        
        for line in lines:
            line = line.strip()
            # Пропускаем пустые строки и служебные сообщения
            if not line or line.startswith('...') or 'Thinking' in line:
                continue
            explanation_lines.append(line)
        
        # Объединяем оставшиеся строки
        explanation = ' '.join(explanation_lines)
            
        return explanation

# Использование
explainer = ProofExplainer()

# Пример доказательства
proof_steps = [
    "Шаг 1: Унификация {x/Сократ} в ¬Человек(x) ∨ Смертен(x)",
    "Шаг 2: Резолюция с Человек(Сократ) -> Смертен(Сократ)", 
    "Шаг 3: Резолюция Смертен(Сократ) и ¬Смертен(Сократ) -> Противоречие"
]

print("Входные шаги доказательства:")
for step in proof_steps:
    print(f"  - {step}")

print("\nГенерируем объяснение...")
explanation = explainer.explain_proof(proof_steps)

print("\nОбъяснение:")
print(explanation)