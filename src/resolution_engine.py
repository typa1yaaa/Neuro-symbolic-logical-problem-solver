"""
Модуль для доказательства методом резолюций в логике предикатов первого порядка.
Реализует алгоритм резолюции с унификацией для автоматического доказательства
теорем в логике предикатов первого порядка.
"""

import re
from typing import List, Tuple, Dict, Optional, Any, Set


class ResolutionEngine:
    """
    Движок резолюций для логики предикатов первого порядка.
    
    Реализует алгоритм резолюции с подробным логированием всех шагов,
    включая унификацию, применение подстановок и проверку на противоречие.
    
    Атрибуты:
        steps_log (List[Dict]): Лог всех шагов доказательства
        step_counter (int): Счетчик шагов резолюции
        clause_registry (Dict[int, Dict]): Регистр всех клауз с метаданными
        next_clause_id (int): Следующий доступный ID для клаузы
    """

    def __init__(self):
        """Инициализация движка резолюций с пустыми структурами данных."""
        self.steps_log = []  # Лог всех шагов резолюции
        self.step_counter = 0  # Счетчик шагов
        self.clause_registry = {}  # Регистр клауз: id -> {clause, source, parents}
        self.next_clause_id = 0  # Счетчик для назначения ID клаузам

    def prove(self, clauses: List[str]) -> Tuple[bool, List[Dict]]:
        """
        Основной метод доказательства методом резолюций.
        
        Принимает множество клауз и пытается вывести противоречие (пустую клаузу).
        
        Args:
            clauses: Список дизъюнктов в строковом формате, например:
                    ["P(x) ∨ Q(y)", "¬P(a)", "¬Q(b)"]
        
        Returns:
            Tuple[bool, List[Dict]]: 
                - bool: True если доказательство успешно (найдено противоречие)
                - List[Dict]: Подробный лог всех шагов доказательства
        
        Пример:
            >>> engine = ResolutionEngine()
            >>> success, log = engine.prove(["P(x)", "¬P(a)"])
            >>> print(success)
            True
        """
        # Инициализация состояния движка для нового доказательства
        self.steps_log = []
        self.step_counter = 0
        self.clause_registry = {}
        self.next_clause_id = 0

        try:
            # Шаг 1: Парсинг входных клауз
            parsed_clauses = [self._parse_clause(clause) for clause in clauses]

            # Шаг 2: Регистрация исходных клауз
            initial_clause_ids = []
            for i, clause in enumerate(parsed_clauses):
                clause_id = self._register_clause(clause, f"Исходная клауза {i+1}")
                initial_clause_ids.append(clause_id)

            # Шаг 3: Логирование начального состояния
            self._log_initial_state(initial_clause_ids, clauses)

            # Шаг 4: Запуск алгоритма резолюции
            result = self._resolution_algorithm(initial_clause_ids)

            return result, self.steps_log

        except Exception as e:
            # Обработка и логирование ошибок
            error_step = {
                'step': 'error',
                'type': 'error',
                'message': f'Ошибка при выполнении резолюции: {str(e)}'
            }
            self.steps_log.append(error_step)
            return False, self.steps_log

    def _parse_clause(self, clause_str: str) -> List[Tuple[str, List[str], bool]]:
        """
        Парсит строковое представление клаузы во внутреннюю структуру.
        
        Внутреннее представление клаузы: список литералов, где каждый литерал -
        это кортеж (предикат, аргументы, отрицание).
        
        Args:
            clause_str: Строка клаузы, например "P(x) ∨ ¬Q(y,z)"
        
        Returns:
            List[Tuple[str, List[str], bool]]: Список литералов клаузы
        
        Пример:
            >>> self._parse_clause("P(x) ∨ ¬Q(a, f(b))")
            [('P', ['x'], False), ('Q', ['a', 'f(b)'], True)]
        """
        clause = []

        # Разделение клаузы на литералы с учетом вложенных скобок
        literals = self._split_literals(clause_str)

        for literal in literals:
            literal = literal.strip()
            if not literal:
                continue

            # Определение отрицания (литерал начинается с '¬')
            negated = literal.startswith('¬')
            if negated:
                literal = literal[1:].strip()  # Удаление символа отрицания

            # Извлечение предиката и аргументов
            pred, args = self._parse_predicate_with_args(literal)
            if pred:
                clause.append((pred, args, negated))

        return clause

    def _split_literals(self, clause_str: str) -> List[str]:
        """
        Разделяет строку клаузы на отдельные литералы.
        
        Учитывает вложенные скобки для корректной обработки функций.
        
        Args:
            clause_str: Строка клаузы с разделителями '∨'
        
        Returns:
            List[str]: Список строк литералов
        
        Пример:
            >>> self._split_literals("P(x) ∨ Q(f(a,b)) ∨ R(z)")
            ['P(x)', 'Q(f(a,b))', 'R(z)']
        """
        literals = []
        current_literal = ""
        bracket_depth = 0  # Глубина вложенности скобок

        for char in clause_str:
            if char == '(':
                bracket_depth += 1
            elif char == ')':
                bracket_depth -= 1
            elif char == '∨' and bracket_depth == 0:
                # Разделитель на верхнем уровне - разделяем литералы
                literals.append(current_literal.strip())
                current_literal = ""
                continue

            current_literal += char

        # Добавление последнего литерала
        if current_literal.strip():
            literals.append(current_literal.strip())

        return literals

    def _parse_predicate_with_args(self, literal: str) -> Tuple[Optional[str], List[str]]:
        """
        Извлекает имя предиката и список аргументов из литерала.
        
        Args:
            literal: Строка литерала без отрицания, например "P(x, f(y))"
        
        Returns:
            Tuple[Optional[str], List[str]]: (предикат, список аргументов)
        
        Пример:
            >>> self._parse_predicate_with_args("P(x, f(a,b))")
            ('P', ['x', 'f(a,b)'])
        """
        # Поиск открывающей скобки с аргументами
        open_bracket_pos = literal.find('(')
        if open_bracket_pos == -1 or not literal.endswith(')'):
            # Литерал без аргументов или с синтаксической ошибкой
            return None, []

        predicate_name = literal[:open_bracket_pos].strip()
        args_string = literal[open_bracket_pos+1:-1]  # Текст между скобками

        # Разделение аргументов с учетом вложенных функций
        arguments = self._split_arguments(args_string)

        return predicate_name, arguments

    def _split_arguments(self, args_str: str) -> List[str]:
        """
        Разделяет строку аргументов на отдельные аргументы.
        
        Учитывает вложенные скобки в функциональных термах.
        
        Args:
            args_str: Строка аргументов, например "x, f(a,b), y"
        
        Returns:
            List[str]: Список аргументов
        
        Пример:
            >>> self._split_arguments("x, f(a,b), y")
            ['x', 'f(a,b)', 'y']
        """
        arguments = []
        current_arg = ""
        bracket_depth = 0

        for char in args_str:
            if char == '(':
                bracket_depth += 1
            elif char == ')':
                bracket_depth -= 1
            elif char == ',' and bracket_depth == 0:
                # Запятая на верхнем уровне - разделитель аргументов
                arguments.append(current_arg.strip())
                current_arg = ""
                continue

            current_arg += char

        # Добавление последнего аргумента
        if current_arg.strip():
            arguments.append(current_arg.strip())

        return arguments

    def _register_clause(self, clause: List[Tuple[str, List[str], bool]], 
                        source: str) -> int:
        """
        Регистрирует клаузу в реестре и возвращает её идентификатор.
        
        Args:
            clause: Внутреннее представление клаузы
            source: Описание источника клаузы
        
        Returns:
            int: Уникальный идентификатор зарегистрированной клаузы
        """
        clause_id = self.next_clause_id
        self.clause_registry[clause_id] = {
            'clause': clause,           # Внутреннее представление
            'string': self._clause_to_string(clause),  # Строковое представление
            'source': source,           # Источник клаузы
            'parents': []               # ID родительских клауз (для резолюции)
        }
        self.next_clause_id += 1
        return clause_id

    def _clause_to_string(self, clause: List[Tuple[str, List[str], bool]]) -> str:
        """
        Конвертирует внутреннее представление клаузы в строку.
        
        Args:
            clause: Внутреннее представление клаузы
        
        Returns:
            str: Строковое представление клаузы
        
        Пример:
            >>> self._clause_to_string([('P', ['x'], False), ('Q', ['y'], True)])
            'P(x) ∨ ¬Q(y)'
        """
        if not clause:  # Пустая клауза - противоречие
            return '□'

        literals = []
        for predicate, args, negated in clause:
            # Форматирование литерала: [¬]предикат(аргументы)
            negation_symbol = '¬' if negated else ''
            arguments_str = ', '.join(args)
            literal_str = f"{negation_symbol}{predicate}({arguments_str})"
            literals.append(literal_str)

        # Соединение литералов дизъюнкцией
        return ' ∨ '.join(literals) if len(literals) > 1 else literals[0]

    def _log_initial_state(self, clause_ids: List[int], original_clauses: List[str]):
        """
        Логирует начальное состояние системы клауз.
        
        Args:
            clause_ids: Список ID исходных клауз
            original_clauses: Оригинальные строковые представления клауз
        """
        clauses_info = []
        for clause_id in clause_ids:
            clause_data = self.clause_registry[clause_id]
            clauses_info.append({
                'id': clause_id,
                'clause': clause_data['string'],
                'source': clause_data['source']
            })

        initial_state_log = {
            'step': 0,
            'type': 'initial',
            'clauses': clauses_info,
            'original_clauses': original_clauses,
            'message': 'Начальное множество клауз'
        }
        self.steps_log.append(initial_state_log)

    def _resolution_algorithm(self, initial_clause_ids: List[int]) -> bool:
        """
        Основной алгоритм резолюции.
        
        Реализует метод резолюции с поиском в ширину. Алгоритм продолжает
        генерировать новые резольвенты до тех пор, пока не будет найдена
        пустая клауза (противоречие) или не исчерпаются возможные резолюции.
        
        Args:
            initial_clause_ids: Список ID исходных клауз
        
        Returns:
            bool: True если найдено противоречие, иначе False
        """
        used_pairs: Set[Tuple[int, int]] = set()  # Множество использованных пар клауз
        all_clause_ids = initial_clause_ids.copy()  # Все известные клаузы

        while True:
            self.step_counter += 1

            # Проверка на наличие пустой клаузы (противоречия)
            contradiction_found = self._check_for_contradiction(all_clause_ids)
            if contradiction_found:
                return True

            # Попытка применить резолюцию к новым парам клауз
            new_clauses_found = self._try_resolutions(all_clause_ids, used_pairs)

            if not new_clauses_found:
                # Не удалось найти новые клаузы - доказательство невозможно
                no_progress_log = {
                    'step': self.step_counter,
                    'type': 'no_new_clauses',
                    'message': 'Новых клауз не найдено - доказательство невозможно'
                }
                self.steps_log.append(no_progress_log)
                return False

            # Защита от бесконечного цикла
            if self.step_counter > 100:
                timeout_log = {
                    'step': self.step_counter,
                    'type': 'timeout',
                    'message': 'Превышено максимальное количество шагов'
                }
                self.steps_log.append(timeout_log)
                return False

    def _check_for_contradiction(self, clause_ids: List[int]) -> bool:
        """
        Проверяет множество клауз на наличие пустой клаузы (противоречия).
        
        Args:
            clause_ids: Список ID проверяемых клауз
        
        Returns:
            bool: True если найдена пустая клауза
        """
        for clause_id in clause_ids:
            clause = self.clause_registry[clause_id]['clause']
            if not clause:  # Пустая клауза □
                contradiction_log = {
                    'step': self.step_counter,
                    'type': 'contradiction_found',
                    'clause_id': clause_id,
                    'clause': '□',
                    'parents': self.clause_registry[clause_id]['parents'],
                    'message': 'Найдена пустая клауза - противоречие!'
                }
                self.steps_log.append(contradiction_log)
                return True
        return False

    def _try_resolutions(self, all_clause_ids: List[int], 
                        used_pairs: Set[Tuple[int, int]]) -> bool:
        """
        Пытается применить резолюцию ко всем возможным парам клауз.
        
        Args:
            all_clause_ids: Список всех ID клауз
            used_pairs: Множество уже использованных пар клауз
        
        Returns:
            bool: True если найдена хотя бы одна новая клауза
        """
        new_clauses_found = False
        n = len(all_clause_ids)

        # Перебор всех возможных пар клауз
        for i in range(n):
            for j in range(i + 1, n):
                clause1_id = all_clause_ids[i]
                clause2_id = all_clause_ids[j]

                # Пропуск уже использованных пар
                if (clause1_id, clause2_id) in used_pairs:
                    continue

                clause1 = self.clause_registry[clause1_id]['clause']
                clause2 = self.clause_registry[clause2_id]['clause']

                # Применение резолюции к паре клауз
                resolvents, unification_logs = self._resolve_clauses(
                    clause1, clause2, clause1_id, clause2_id)

                if resolvents:
                    used_pairs.add((clause1_id, clause2_id))

                    # Обработка найденных резольвент
                    for resolvent, log_entry in zip(resolvents, unification_logs):
                        if self._process_resolvent(resolvent, all_clause_ids, 
                                                 clause1_id, clause2_id, log_entry):
                            new_clauses_found = True

        return new_clauses_found

    def _process_resolvent(self, resolvent: List[Tuple[str, List[str], bool]],
                          all_clause_ids: List[int], clause1_id: int, clause2_id: int,
                          log_entry: Dict) -> bool:
        """
        Обрабатывает найденную резольвенту: проверяет и регистрирует её.
        
        Args:
            resolvent: Резольвента для обработки
            all_clause_ids: Список всех ID клауз (будет дополнен)
            clause1_id: ID первой родительской клаузы
            clause2_id: ID второй родительской клаузы
            log_entry: Информация для логирования
        
        Returns:
            bool: True если резольвента была добавлена
        """
        # Пропуск тавтологий
        if self._is_tautology(resolvent):
            return False

        # Пропуск клауз, которые поглощаются существующими
        if self._is_subsumed(resolvent, all_clause_ids):
            return False

        # Регистрация новой клаузы
        parents = [clause1_id, clause2_id]
        resolvent_id = self._register_clause(resolvent, f"Резольвента шага {self.step_counter}")
        self.clause_registry[resolvent_id]['parents'] = parents

        all_clause_ids.append(resolvent_id)

        # Логирование шага резолюции
        resolution_step_log = {
            'step': self.step_counter,
            'type': 'resolution_step',
            'clause1_id': clause1_id,
            'clause2_id': clause2_id,
            'clause1': self._clause_to_string(self.clause_registry[clause1_id]['clause']),
            'clause2': self._clause_to_string(self.clause_registry[clause2_id]['clause']),
            'resolvent_id': resolvent_id,
            'resolvent': self._clause_to_string(resolvent),
            'unification': log_entry['unification'],
            'literals_resolved': log_entry['literals_resolved'],
            'parents': parents,
            'new_clauses_count': len(all_clause_ids),
            'message': f'Резолюция клауз {clause1_id} и {clause2_id}'
        }
        self.steps_log.append(resolution_step_log)

        return True

    def _resolve_clauses(self, clause1: List[Tuple[str, List[str], bool]],
                        clause2: List[Tuple[str, List[str], bool]],
                        clause1_id: int, clause2_id: int) -> Tuple[List, List]:
        """
        Применяет резолюцию к двум клаузам.
        
        Ищет комплементарные литералы и пытается их унифицировать.
        
        Args:
            clause1: Первая клауза
            clause2: Вторая клауза
            clause1_id: ID первой клаузы (для отладки)
            clause2_id: ID второй клаузы (для отладки)
        
        Returns:
            Tuple[List, List]: (список резольвент, список логов унификации)
        """
        resolvents = []
        unification_logs = []

        # Перебор всех пар литералов из разных клауз
        for i, (pred1, args1, neg1) in enumerate(clause1):
            for j, (pred2, args2, neg2) in enumerate(clause2):
                # Условие резолюции: одинаковые предикаты, разные знаки
                if pred1 == pred2 and neg1 != neg2:
                    # Попытка унификации аргументов
                    substitution = self._unify(args1, args2)

                    if substitution is not None:
                        # Успешная унификация - создаем резольвенту
                        resolvent = self._create_resolvent(
                            clause1, clause2, i, j, substitution)

                        resolvents.append(resolvent)

                        # Сохранение информации об унификации для лога
                        log_entry = {
                            'unification': substitution,
                            'literals_resolved': [
                                (f'{"¬" if neg1 else ""}{pred1}({", ".join(args1)})', i),
                                (f'{"¬" if neg2 else ""}{pred2}({", ".join(args2)})', j)
                            ]
                        }
                        unification_logs.append(log_entry)

        return resolvents, unification_logs

    def _create_resolvent(self, clause1: List[Tuple[str, List[str], bool]],
                         clause2: List[Tuple[str, List[str], bool]],
                         idx1: int, idx2: int,
                         substitution: Dict[str, str]) -> List[Tuple[str, List[str], bool]]:
        """
        Создает резольвенту из двух клауз с применением подстановки.
        
        Args:
            clause1: Первая клауза
            clause2: Вторая клауза
            idx1: Индекс разрешаемого литерала в первой клаузе
            idx2: Индекс разрешаемого литерала во второй клаузе
            substitution: Подстановка для унификации
        
        Returns:
            List[Tuple]: Новая резольвента
        """
        # Применение подстановки к обеим клаузам
        substituted_clause1 = self._apply_substitution(clause1, substitution)
        substituted_clause2 = self._apply_substitution(clause2, substitution)

        # Создание резольвенты: объединение без разрешаемых литералов
        resolvent = []

        # Добавление литералов из первой клаузы (кроме разрешаемого)
        for k, literal in enumerate(substituted_clause1):
            if k != idx1:
                if literal not in resolvent:  # Избегание дубликатов
                    resolvent.append(literal)

        # Добавление литералов из второй клаузы (кроме разрешаемого)
        for k, literal in enumerate(substituted_clause2):
            if k != idx2:
                if literal not in resolvent:  # Избегание дубликатов
                    resolvent.append(literal)

        return resolvent

    def _unify(self, args1: List[str], args2: List[str]) -> Optional[Dict[str, str]]:
        """
        Унифицирует два списка аргументов.
        
        Алгоритм унификации Робинсона для нахождения подстановки,
        делающей два терма идентичными.
        
        Args:
            args1: Список аргументов первого литерала
            args2: Список аргументов второго литерала
        
        Returns:
            Optional[Dict[str, str]]: Подстановка или None если унификация невозможна
        
        Пример:
            >>> self._unify(['x', 'a'], ['b', 'y'])
            {'x': 'b', 'y': 'a'}
        """
        if len(args1) != len(args2):
            return None  # Разное количество аргументов

        substitution = {}

        for term1, term2 in zip(args1, args2):
            # Случай 1: Оба терма - константы
            if self._is_constant(term1) and self._is_constant(term2):
                if term1 != term2:
                    return None  # Разные константы не унифицируемы

            # Случай 2: Переменная и произвольный терм
            elif self._is_variable(term1):
                if term1 in substitution:
                    # Переменная уже имеет подстановку - рекурсивная унификация
                    if not self._unify_terms(substitution[term1], term2, substitution):
                        return None
                else:
                    # Новая подстановка: переменная -> терм
                    substitution[term1] = term2

            # Случай 3: Произвольный терм и переменная
            elif self._is_variable(term2):
                if term2 in substitution:
                    if not self._unify_terms(term1, substitution[term2], substitution):
                        return None
                else:
                    substitution[term2] = term1

            # Случай 4: Оба терма содержат функции
            elif self._contains_function(term1) or self._contains_function(term2):
                # Упрощенная проверка: только точное совпадение
                if term1 != term2:
                    return None

            # Случай 5: Любой другой случай (не должен происходить)
            else:
                return None

        return substitution

    def _unify_terms(self, term1: str, term2: str, 
                    substitution: Dict[str, str]) -> bool:
        """
        Рекурсивно унифицирует два терма с учетом текущей подстановки.
        
        Args:
            term1: Первый терм
            term2: Второй терм
            substitution: Текущая подстановка (модифицируется)
        
        Returns:
            bool: True если унификация успешна
        """
        # Применяем существующие подстановки к термам
        resolved_term1 = self._apply_substitution_to_term(term1, substitution)
        resolved_term2 = self._apply_substitution_to_term(term2, substitution)

        # Базовые случаи унификации
        if resolved_term1 == resolved_term2:
            return True
        elif self._is_variable(resolved_term1):
            substitution[resolved_term1] = resolved_term2
            return True
        elif self._is_variable(resolved_term2):
            substitution[resolved_term2] = resolved_term1
            return True
        else:
            return False

    def _apply_substitution_to_term(self, term: str, 
                                  substitution: Dict[str, str]) -> str:
        """
        Применяет подстановку к одиночному терму.
        
        Args:
            term: Исходный терм
            substitution: Подстановка для применения
        
        Returns:
            str: Терм после применения подстановки
        """
        result = term
        for var, value in substitution.items():
            if result == var:
                result = value
            elif var in result:
                # Замена переменных внутри сложных термов
                result = result.replace(var, value)
        return result

    def _apply_substitution(self, clause: List[Tuple[str, List[str], bool]],
                          substitution: Dict[str, str]) -> List[Tuple[str, List[str], bool]]:
        """
        Применяет подстановку ко всем термам в клаузе.
        
        Args:
            clause: Исходная клауза
            substitution: Подстановка для применения
        
        Returns:
            List[Tuple]: Клауза после применения подстановки
        """
        substituted_clause = []
        for predicate, args, negated in clause:
            substituted_args = [self._apply_substitution_to_term(arg, substitution) 
                              for arg in args]
            substituted_clause.append((predicate, substituted_args, negated))
        return substituted_clause

    def _is_constant(self, term: str) -> bool:
        """
        Проверяет, является ли терм константой.
        
        Константы начинаются с заглавной буквы и не содержат скобок.
        
        Args:
            term: Проверяемый терм
        
        Returns:
            bool: True если терм - константа
        """
        return (term and 
                term[0].isupper() and 
                '(' not in term)

    def _is_variable(self, term: str) -> bool:
        """
        Проверяет, является ли терм переменной.
        
        Переменные начинаются с строчной буквы и не содержат скобок.
        
        Args:
            term: Проверяемый терм
        
        Returns:
            bool: True если терм - переменная
        """
        return (term and 
                term[0].islower() and 
                not term.isdigit() and
                '(' not in term)

    def _contains_function(self, term: str) -> bool:
        """
        Проверяет, содержит ли терм функциональный символ.
        
        Args:
            term: Проверяемый терм
        
        Returns:
            bool: True если терм содержит функцию (скобки)
        """
        return '(' in term and ')' in term

    def _is_tautology(self, clause: List[Tuple[str, List[str], bool]]) -> bool:
        """
        Проверяет, является ли клауза тавтологией.
        
        Тавтология содержит комплементарные литералы (P и ¬P).
        
        Args:
            clause: Проверяемая клауза
        
        Returns:
            bool: True если клауза - тавтология
        """
        positive_literals = set()
        negative_literals = set()

        for predicate, args, negated in clause:
            # Ключ литерала: (предикат, кортеж аргументов)
            literal_key = (predicate, tuple(args))
            if negated:
                negative_literals.add(literal_key)
            else:
                positive_literals.add(literal_key)

        # Тавтология если есть пересечение положительных и отрицательных литералов
        return bool(positive_literals & negative_literals)

    def _is_subsumed(self, clause: List[Tuple[str, List[str], bool]], 
                    all_clause_ids: List[int]) -> bool:
        """
        Проверяет, поглощается ли клауза существующими клаузами.
        
        Клауза A поглощается клаузой B если A является подмножеством B
        с учетом некоторой подстановки.
        
        Args:
            clause: Проверяемая клауза
            all_clause_ids: Список ID всех существующих клауз
        
        Returns:
            bool: True если клауза поглощается
        """
        for existing_id in all_clause_ids:
            existing_clause = self.clause_registry[existing_id]['clause']
            if self._subsumes(existing_clause, clause):
                return True
        return False

    def _subsumes(self, clause1: List[Tuple[str, List[str], bool]], 
                 clause2: List[Tuple[str, List[str], bool]]) -> bool:
        """
        Проверяет, поглощает ли clause1 clause2.
        
        Упрощенная проверка: точное совпадение клауз.
        В полной реализации должна учитывать подстановки.
        
        Args:
            clause1: Потенциально поглощающая клауза
            clause2: Потенциально поглощаемая клауза
        
        Returns:
            bool: True если clause1 поглощает clause2
        """
        # Упрощенная реализация: проверка точного совпадения
        return clause1 == clause2