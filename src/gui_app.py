import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from logic_formalizer import LogicFormalizer
from resolution_engine import ResolutionEngine
from proof_explainer import ProofExplainer

class LogicProofApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система логического доказательства")
        self.root.geometry("900x700")
        
        # Инициализация компонентов
        self.formalizer = LogicFormalizer()
        self.resolution_engine = ResolutionEngine()
        self.explainer = ProofExplainer()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Создание интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Система логического доказательства методом резолюций",
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Ввод логического высказывания
        ttk.Label(main_frame, text="Введите логическое высказывание:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(main_frame, height=4, width=80)
        self.input_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        self.prove_button = ttk.Button(button_frame, text="Доказать высказывание", 
                                      command=self.start_proof_process)
        self.prove_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Очистить", 
                                      command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Вкладка 1: Формализованные формулы
        self.formulas_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.formulas_frame, text="Формализованные формулы")
        
        ttk.Label(self.formulas_frame, text="Формулы логики предикатов:").pack(anchor=tk.W)
        self.formulas_text = scrolledtext.ScrolledText(self.formulas_frame, height=6)
        self.formulas_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Вкладка 2: Детали доказательства
        self.proof_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.proof_frame, text="Детали доказательства")
        
        ttk.Label(self.proof_frame, text="Пошаговое доказательство:").pack(anchor=tk.W)
        self.proof_text = scrolledtext.ScrolledText(self.proof_frame, height=8)
        self.proof_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Вкладка 3: Объяснение
        self.explanation_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.explanation_frame, text="Объяснение")
        
        ttk.Label(self.explanation_frame, text="Объяснение доказательства простым языком:").pack(anchor=tk.W)
        self.explanation_text = scrolledtext.ScrolledText(self.explanation_frame, height=6)
        self.explanation_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Примеры высказываний
        self.setup_examples_section(main_frame)
    
    def setup_examples_section(self, parent):
        """Секция с примерами высказываний"""
        examples_frame = ttk.LabelFrame(parent, text="Примеры высказываний", padding="5")
        examples_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        examples = [
            "Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.",
            "Все кошки — животные. Мурка — кошка. Докажи, что Мурка — животное.",
            "Все честные люди говорят правду. Джон лжет. Докажи, что Джон не честный человек.",
            "Все птицы летают. Пингвин не летает. Значит, пингвин не птица."
        ]
        
        for i, example in enumerate(examples):
            btn = ttk.Button(examples_frame, text=f"Пример {i+1}", 
                           command=lambda ex=example: self.load_example(ex))
            btn.grid(row=i//2, column=i%2, padx=5, pady=2, sticky=tk.W)
    
    def load_example(self, example):
        """Загрузка примера в поле ввода"""
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, example)
    
    def clear_all(self):
        """Очистка всех полей"""
        self.input_text.delete(1.0, tk.END)
        self.formulas_text.delete(1.0, tk.END)
        self.proof_text.delete(1.0, tk.END)
        self.explanation_text.delete(1.0, tk.END)
        self.status_var.set("Готов к работе")
    
    def start_proof_process(self):
        """Запуск процесса доказательства в отдельном потоке"""
        user_input = self.input_text.get(1.0, tk.END).strip()
        if not user_input:
            messagebox.showwarning("Предупреждение", "Введите логическое высказывание")
            return
        
        # Блокируем кнопку и запускаем прогресс
        self.prove_button.config(state='disabled')
        self.progress.start()
        self.status_var.set("Начинаем доказательство...")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.run_proof_process, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def run_proof_process(self, user_input):
        """Основной процесс доказательства"""
        try:
            # Шаг 1: Формализация
            self.update_status("Формализуем высказывание...")
            formulas = self.formalizer.formalize_problem(user_input)
            
            # Обновляем UI в основном потоке
            self.root.after(0, self.update_formulas_tab, formulas)
            
            if "Ошибка" in str(formulas[0]) or "Не удалось" in str(formulas[0]):
                self.root.after(0, self.show_error, f"Ошибка формализации: {formulas[0]}")
                return
            
            # Шаг 2: Доказательство методом резолюций
            self.update_status("Применяем метод резолюций...")
            success, proof_log = self.resolution_engine.prove(formulas)
            
            # Обновляем UI в основном потоке
            self.root.after(0, self.update_proof_tab, success, proof_log)
            
            # Шаг 3: Генерация объяснения
            self.update_status("Генерируем объяснение...")
            explanation = self.generate_explanation(proof_log, success)
            
            # Обновляем UI в основном потоке
            self.root.after(0, self.update_explanation_tab, explanation, success)
            
            self.update_status("Доказательство завершено!")
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Ошибка: {str(e)}")
        finally:
            # Восстанавливаем интерфейс
            self.root.after(0, self.proof_complete)
    
    def update_status(self, message):
        """Обновление статуса в основном потоке"""
        self.root.after(0, lambda: self.status_var.set(message))
    
    def update_formulas_tab(self, formulas):
        """Обновление вкладки с формулами"""
        self.formulas_text.delete(1.0, tk.END)
        if isinstance(formulas, list):
            for i, formula in enumerate(formulas, 1):
                self.formulas_text.insert(tk.END, f"{i}. {formula}\n")
        else:
            self.formulas_text.insert(tk.END, str(formulas))
    
    def update_proof_tab(self, success, proof_log):
        """Обновление вкладки с доказательством"""
        self.proof_text.delete(1.0, tk.END)
        
        if not proof_log:
            self.proof_text.insert(tk.END, "Не удалось получить лог доказательства")
            return
        
        result_text = "✅ ДОКАЗАТЕЛЬСТВО УСПЕШНО!\n\n" if success else "❌ ДОКАЗАТЕЛЬСТВО НЕ УДАЛОСЬ\n\n"
        self.proof_text.insert(tk.END, result_text)
        
        for step in proof_log:
            step_type = step.get('type', 'unknown')
            
            if step_type == 'initial':
                self.proof_text.insert(tk.END, "ИСХОДНЫЕ КЛАУЗЫ:\n")
                for clause_info in step.get('clauses', []):
                    self.proof_text.insert(tk.END, f"  {clause_info['id']}. {clause_info['clause']}\n")
                self.proof_text.insert(tk.END, "\n")
            
            elif step_type == 'resolution_step':
                clause1_id = step.get('clause1_id', '?')
                clause2_id = step.get('clause2_id', '?')
                resolvent_id = step.get('resolvent_id', '?')
                resolvent = step.get('resolvent', '')
                unification = step.get('unification', {})
                
                self.proof_text.insert(tk.END, f"Шаг {step.get('step', '?')}: Резолюция {clause1_id} и {clause2_id}\n")
                self.proof_text.insert(tk.END, f"  Резольвента {resolvent_id}: {resolvent}\n")
                if unification:
                    self.proof_text.insert(tk.END, f"  Унификация: {unification}\n")
                self.proof_text.insert(tk.END, "\n")
            
            elif step_type == 'contradiction_found':
                clause_id = step.get('clause_id', '?')
                parents = step.get('parents', [])
                self.proof_text.insert(tk.END, f"🎯 НАЙДЕНА ПУСТАЯ КЛАУЗА {clause_id}!\n")
                self.proof_text.insert(tk.END, f"Получена из клауз: {parents}\n")
                self.proof_text.insert(tk.END, "ДОКАЗАТЕЛЬСТВО ЗАВЕРШЕНО - ПРОТИВОРЕЧИЕ!\n\n")
            
            elif step_type in ['no_new_clauses', 'timeout', 'error']:
                self.proof_text.insert(tk.END, f"ℹ️ {step.get('message', '')}\n\n")
    
    def generate_explanation(self, proof_log, success):
        """Генерация объяснения на основе лога доказательства"""
        if not proof_log:
            return "Не удалось сгенерировать объяснение для пустого лога доказательства"
        
        # Собираем ключевые шаги для объяснения
        proof_steps = []
        
        for step in proof_log:
            step_type = step.get('type', '')
            
            if step_type == 'resolution_step':
                clause1 = step.get('clause1', '')
                clause2 = step.get('clause2', '')
                resolvent = step.get('resolvent', '')
                unification = step.get('unification', {})
                
                step_desc = f"Резолюция '{clause1}' и '{clause2}'"
                if unification:
                    step_desc += f" с унификацией {unification}"
                step_desc += f" -> '{resolvent}'"
                proof_steps.append(step_desc)
            
            elif step_type == 'contradiction_found':
                proof_steps.append("Найдено противоречие (пустая клауза) - доказательство завершено")
        
        # Если шагов слишком много, берем только ключевые
        if len(proof_steps) > 5:
            key_steps = [proof_steps[0], "... промежуточные шаги ...", proof_steps[-1]]
        else:
            key_steps = proof_steps
        
        explanation = self.explainer.explain_proof(key_steps)
        return explanation
    
    def update_explanation_tab(self, explanation, success):
        """Обновление вкладки с объяснением"""
        self.explanation_text.delete(1.0, tk.END)
        
        result_marker = "✅ ДОКАЗАНО! " if success else "❒ РЕЗУЛЬТАТ: "
        self.explanation_text.insert(tk.END, result_marker)
        
        if explanation and "Ошибка" not in explanation:
            self.explanation_text.insert(tk.END, explanation)
        else:
            default_explanation = """
Доказательство методом резолюций основано на поиске противоречия в множестве формул. 
Мы последовательно применяем правило резолюции к парам формул, пытаясь вывести пустую клаузу (□). 
Нахождение пустой клаузы означает, что исходное предположение ведет к противоречию, 
что доказывает истинность доказываемого утверждения.
            """
            self.explanation_text.insert(tk.END, default_explanation.strip())
    
    def proof_complete(self):
        """Завершение процесса доказательства"""
        self.progress.stop()
        self.prove_button.config(state='normal')
    
    def show_error(self, message):
        """Показать сообщение об ошибке"""
        messagebox.showerror("Ошибка", message)
        self.proof_complete()
        self.status_var.set("Ошибка при выполнении")

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = LogicProofApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()