from proof_explainer import ProofExplainer

explainer = ProofExplainer(model_name="deepseek-v3.1:671b-cloud")


def show_test(steps: list, success: bool = True):
    print("\nВходные шаги доказательства:")
    for i, step in enumerate(steps, 1):
        if isinstance(step, dict):
            print(f"   {i}. {step.get('message', 'Шаг без описания')}")
        else:
            print(f"   {i}. {step}")

    print("\nГенерируется объяснение...\n")
    explanation = explainer.explain_proof(steps, success)

    print("Объяснение на естественном языке:")
    print("-" * 70)
    print(explanation)
    print("=" * 80 + "\n")


# 1. Сократ смертен
def test_socrates_mortal():
    print("1. КЛАССИЧЕСКИЙ СИЛЛОГИЗМ: Сократ — человек → Сократ смертен")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Человек(x) ∨ Смертен(x)', 'source': 'аксиома'},
                {'id': 2, 'clause': 'Человек(Сократ)', 'source': 'факт'},
                {'id': 3, 'clause': '¬Смертен(Сократ)', 'source': 'отрицание цели'}
            ],
            'message': 'Исходные клаузы: все люди смертны, Сократ - человек, отрицание смертности Сократа'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 1,
            'clause2_id': 2,
            'clause1': '¬Человек(x) ∨ Смертен(x)',
            'clause2': 'Человек(Сократ)',
            'resolvent': 'Смертен(Сократ)',
            'resolvent_id': 4,
            'unification': {'x': 'Сократ'},
            'parents': [1, 2],
            'message': 'Унификация {x/Сократ} в ¬Человек(x) ∨ Смертен(x) и резолюция с Человек(Сократ) → получаем Смертен(Сократ)'
        },
        {
            'step': 3,
            'type': 'contradiction_found',
            'clause1_id': 4,
            'clause2_id': 3,
            'clause1': 'Смертен(Сократ)',
            'clause2': '¬Смертен(Сократ)',
            'resolvent': '□',
            'message': 'Резолюция Смертен(Сократ) и ¬Смертен(Сократ) → Пустая клауза (противоречие)',
            'parents': [4, 3]
        }
    ]
    show_test(steps, success=True)



# 2 Джон лжёт → Джон нечестный
def test_john_liar():
    print("2. ДЖОН ЛЖЁТ → Джон нечестный")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Честный(x) ∨ ГоворитПравду(x)', 'source': 'аксиома'},
                {'id': 2, 'clause': '¬ГоворитПравду(Джон)', 'source': 'факт'},
                {'id': 3, 'clause': 'Честный(Джон)', 'source': 'отрицание цели'}
            ],
            'message': 'Исходные клаузы: честные говорят правду, Джон не говорит правду, отрицание нечестности Джона'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 1,
            'clause2_id': 2,
            'clause1': '¬Честный(x) ∨ ГоворитПравду(x)',
            'clause2': '¬ГоворитПравду(Джон)',
            'resolvent': '¬Честный(Джон)',
            'resolvent_id': 4,
            'unification': {'x': 'Джон'},
            'parents': [1, 2],
            'message': 'Резолюция ¬Честный(x) ∨ ГоворитПравду(x) и ¬ГоворитПравду(Джон) → ¬Честный(Джон)'
        },
        {
            'step': 3,
            'type': 'contradiction_found',
            'clause1_id': 4,
            'clause2_id': 3,
            'clause1': '¬Честный(Джон)',
            'clause2': 'Честный(Джон)',
            'resolvent': '□',
            'message': 'Резолюция с Честный(Джон) → Противоречие',
            'parents': [4, 3]
        }
    ]
    show_test(steps, success=True)



# 3 Пингвин не летает → Пингвин не птица
def test_penguin_not_bird():
    print("3. ПИНГВИН НЕ ЛЕТАЕТ → Пингвин не птица")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Птица(x) ∨ Летает(x)', 'source': 'аксиома'},
                {'id': 2, 'clause': '¬Летает(Пингвин)', 'source': 'факт'},
                {'id': 3, 'clause': 'Птица(Пингвин)', 'source': 'отрицание цели'}
            ],
            'message': 'Исходные клаузы: птицы летают, пингвин не летает, отрицание того что пингвин не птица'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 1,
            'clause2_id': 2,
            'clause1': '¬Птица(x) ∨ Летает(x)',
            'clause2': '¬Летает(Пингвин)',
            'resolvent': '¬Птица(Пингвин)',
            'resolvent_id': 4,
            'unification': {'x': 'Пингвин'},
            'parents': [1, 2],
            'message': 'Резолюция ¬Птица(x) ∨ Летает(x) и ¬Летает(Пингвин) → ¬Птица(Пингвин)'
        },
        {
            'step': 3,
            'type': 'contradiction_found',
            'clause1_id': 4,
            'clause2_id': 3,
            'clause1': '¬Птица(Пингвин)',
            'clause2': 'Птица(Пингвин)',
            'resolvent': '□',
            'message': 'Резолюция с Птица(Пингвин) → Противоречие',
            'parents': [4, 3]
        }
    ]
    show_test(steps, success=True)


# 4 Не сдал экзамен → Не готовился
def test_contraposition_exam():
    print("4.: Не сдал экзамен → Не готовился")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Подготовился(x) ∨ СдалЭкзамен(x)', 'source': 'аксиома'},
                {'id': 2, 'clause': '¬СдалЭкзамен(Петя)', 'source': 'факт'},
                {'id': 3, 'clause': 'Подготовился(Петя)', 'source': 'отрицание цели'}
            ],
            'message': 'Исходные клаузы: подготовившиеся сдают экзамен, Петя не сдал экзамен, отрицание того что Петя не подготовился'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 1,
            'clause2_id': 2,
            'clause1': '¬Подготовился(x) ∨ СдалЭкзамен(x)',
            'clause2': '¬СдалЭкзамен(Петя)',
            'resolvent': '¬Подготовился(Петя)',
            'resolvent_id': 4,
            'unification': {'x': 'Петя'},
            'parents': [1, 2],
            'message': 'Резолюция ¬Подготовился(x) ∨ СдалЭкзамен(x) и ¬СдалЭкзамен(Петя) → ¬Подготовился(Петя)'
        },
        {
            'step': 3,
            'type': 'contradiction_found',
            'clause1_id': 4,
            'clause2_id': 3,
            'clause1': '¬Подготовился(Петя)',
            'clause2': 'Подготовился(Петя)',
            'resolvent': '□',
            'message': 'Резолюция с Подготовился(Петя) → Противоречие',
            'parents': [4, 3]
        }
    ]
    show_test(steps, success=True)


# 5 Только Маша — отличница
def test_only_masha():
    print("5. «ТОЛЬКО МАША» сдала на 5 → только Маша отличница")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Отличник(x) ∨ СдалНа5(x)', 'source': 'аксиома'},
                {'id': 2, 'clause': '¬СдалНа5(y) ∨ y = Маша', 'source': 'аксиома'},
                {'id': 3, 'clause': 'СдалНа5(Маша)', 'source': 'факт'}
            ],
            'message': 'Исходные клаузы: отличники сдали на 5, только Маша сдала на 5, Маша сдала на 5'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 1,
            'clause2_id': 2,
            'clause1': '¬Отличник(x) ∨ СдалНа5(x)',
            'clause2': '¬СдалНа5(y) ∨ y = Маша',
            'resolvent': '¬Отличник(x) ∨ x = Маша',
            'resolvent_id': 4,
            'unification': {'y': 'x'},
            'parents': [1, 2],
            'message': 'Резолюция ¬Отличник(x) ∨ СдалНа5(x) и ¬СдалНа5(y) ∨ y = Маша → ¬Отличник(x) ∨ x = Маша'
        },
        {
            'step': 3,
            'type': 'resolution_step',
            'clause1_id': 4,
            'clause2_id': 3,
            'clause1': '¬Отличник(x) ∨ x = Маша',
            'clause2': 'СдалНа5(Маша)',
            'resolvent': '∀x (Отличник(x) ↔ x = Маша)',
            'resolvent_id': 5,
            'unification': {},
            'parents': [4, 3],
            'message': 'Объединение условий доказывает ∀x (Отличник(x) ↔ x = Маша)'
        },
        {
            'step': 4,
            'type': 'success',
            'message': 'Резолюции доказывают ∀x (Отличник(x) ↔ x = Маша)',
            'conclusion': 'Только Маша является отличником'
        }
    ]
    show_test(steps, success=True)


# 6 Закон де Моргана
def test_de_morgan_wizard():
    print("6. ЗАКОН ДЕ МОРГАНА: волшебник не может быть одновременно магом и колдуном")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Волшебник(x) ∨ ¬Маг(x) ∨ ¬Колдун(x)', 'source': 'аксиома'},
                {'id': 2, 'clause': 'Волшебник(Мерлин)', 'source': 'факт'},
                {'id': 3, 'clause': 'Маг(Мерлин)', 'source': 'отрицание цели'},
                {'id': 4, 'clause': 'Колдун(Мерлин)', 'source': 'отрицание цели'}
            ],
            'message': 'Исходные клаузы: волшебник не может быть магом и колдуном одновременно, Мерлин - волшебник, отрицание ограничений'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 1,
            'clause2_id': 2,
            'clause1': '¬Волшебник(x) ∨ ¬Маг(x) ∨ ¬Колдун(x)',
            'clause2': 'Волшебник(Мерлин)',
            'resolvent': '¬Маг(Мерлин) ∨ ¬Колдун(Мерлин)',
            'resolvent_id': 5,
            'unification': {'x': 'Мерлин'},
            'parents': [1, 2],
            'message': 'Резолюция ¬Волшебник(x) ∨ ¬Маг(x) ∨ ¬Колдун(x) и Волшебник(Мерлин) → ¬Маг(Мерлин) ∨ ¬Колдун(Мерлин)'
        },
        {
            'step': 3,
            'type': 'resolution_step',
            'clause1_id': 5,
            'clause2_id': 3,
            'clause1': '¬Маг(Мерлин) ∨ ¬Колдун(Мерлин)',
            'clause2': 'Маг(Мерлин)',
            'resolvent': '¬Колдун(Мерлин)',
            'resolvent_id': 6,
            'unification': {},
            'parents': [5, 3],
            'message': 'Резолюция с Маг(Мерлин) → ¬Колдун(Мерлин)'
        },
        {
            'step': 4,
            'type': 'contradiction_found',
            'clause1_id': 6,
            'clause2_id': 4,
            'clause1': '¬Колдун(Мерлин)',
            'clause2': 'Колдун(Мерлин)',
            'resolvent': '□',
            'message': 'Отрицание цели Маг(Мерлин) ∧ Колдун(Мерлин) → противоречие',
            'parents': [6, 4]
        }
    ]
    show_test(steps, success=True)


# 7 Цепочка импликаций:
def test_rain_accidents_chain():
    print("7. Дождь → Мокрые улицы → Скользко → Аварии")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Дождь ∨ МокрыеУлицы', 'source': 'аксиома'},
                {'id': 2, 'clause': '¬МокрыеУлицы ∨ СкользятМашины', 'source': 'аксиома'},
                {'id': 3, 'clause': '¬СкользятМашины ∨ Аварии', 'source': 'аксиома'},
                {'id': 4, 'clause': 'Дождь', 'source': 'факт'},
                {'id': 5, 'clause': '¬Аварии', 'source': 'отрицание цели'}
            ],
            'message': 'Исходные клаузы: цепочка импликаций дождь→мокрые улицы→скользко→аварии, идет дождь, отрицание аварий'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 1,
            'clause2_id': 4,
            'clause1': '¬Дождь ∨ МокрыеУлицы',
            'clause2': 'Дождь',
            'resolvent': 'МокрыеУлицы',
            'resolvent_id': 6,
            'unification': {},
            'parents': [1, 4],
            'message': 'Резолюция ¬Дождь ∨ МокрыеУлицы и Дождь → МокрыеУлицы'
        },
        {
            'step': 3,
            'type': 'resolution_step',
            'clause1_id': 2,
            'clause2_id': 6,
            'clause1': '¬МокрыеУлицы ∨ СкользятМашины',
            'clause2': 'МокрыеУлицы',
            'resolvent': 'СкользятМашины',
            'resolvent_id': 7,
            'unification': {},
            'parents': [2, 6],
            'message': 'Резолюция ¬МокрыеУлицы ∨ СкользятМашины и МокрыеУлицы → СкользятМашины'
        },
        {
            'step': 4,
            'type': 'resolution_step',
            'clause1_id': 3,
            'clause2_id': 7,
            'clause1': '¬СкользятМашины ∨ Аварии',
            'clause2': 'СкользятМашины',
            'resolvent': 'Аварии',
            'resolvent_id': 8,
            'unification': {},
            'parents': [3, 7],
            'message': 'Резолюция ¬СкользятМашины ∨ Аварии и СкользятМашины → Аварии'
        },
        {
            'step': 5,
            'type': 'contradiction_found',
            'clause1_id': 8,
            'clause2_id': 5,
            'clause1': 'Аварии',
            'clause2': '¬Аварии',
            'resolvent': '□',
            'message': 'Резолюция с ¬Аварии → Противоречие',
            'parents': [8, 5]
        }
    ]
    show_test(steps, success=True)



# 8 Рыцари и лжецы — только Ланселот знает правду
def test_knights_liars_lancelot():
    print("8. Только Ланселот знает правду → он не лжёт")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Рыцарь(x) ∨ ¬Лжёт(x)', 'source': 'аксиома'},
                {'id': 2, 'clause': '¬Лжёт(x) ∨ ¬Рыцарь(x)', 'source': 'аксиома'},
                {'id': 3, 'clause': '¬ЗнаетПравду(x) ∨ ¬Лжёт(x)', 'source': 'аксиома'},
                {'id': 4, 'clause': '∀y (y ≠ Ланселот → ¬ЗнаетПравду(y))', 'source': 'аксиома'},
                {'id': 5, 'clause': 'ЗнаетПравду(Ланселот)', 'source': 'факт'},
                {'id': 6, 'clause': 'Лжёт(Ланселот)', 'source': 'отрицание цели'}
            ],
            'message': 'Исходные клаузы: правила рыцарей и лжецов, только Ланселот знает правду, отрицание того что Ланселот не лжет'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 3,
            'clause2_id': 5,
            'clause1': '¬ЗнаетПравду(x) ∨ ¬Лжёт(x)',
            'clause2': 'ЗнаетПравду(Ланселот)',
            'resolvent': '¬Лжёт(Ланселот)',
            'resolvent_id': 7,
            'unification': {'x': 'Ланселот'},
            'parents': [3, 5],
            'message': 'Резолюция ЗнаетПравду(x) → ¬Лжёт(x) и ЗнаетПравду(Ланселот) → ¬Лжёт(Ланселот)'
        },
        {
            'step': 3,
            'type': 'contradiction_found',
            'clause1_id': 7,
            'clause2_id': 6,
            'clause1': '¬Лжёт(Ланселот)',
            'clause2': 'Лжёт(Ланселот)',
            'resolvent': '□',
            'message': 'Доказываем ¬Лжёт(Ланселот) - противоречие с отрицанием цели',
            'parents': [7, 6]
        }
    ]
    show_test(steps, success=True)


# 9 Транзитивность отношения
def test_transitivity_age():
    print("9. ТРАНЗИТИВНОСТЬ: Маша > Катя > Лена → Маша > Лена")
    print("=" * 70)
    steps = [
        {
            'step': 1,
            'type': 'initial',
            'clauses': [
                {'id': 1, 'clause': '¬Старше(x,y) ∨ ¬Старше(y,z) ∨ Старше(x,z)', 'source': 'аксиома'},
                {'id': 2, 'clause': 'Старше(Маша, Катя)', 'source': 'факт'},
                {'id': 3, 'clause': 'Старше(Катя, Лена)', 'source': 'факт'},
                {'id': 4, 'clause': '¬Старше(Маша, Лена)', 'source': 'отрицание цели'}
            ],
            'message': 'Исходные клаузы: транзитивность старше, Маша старше Кати, Катя старше Лены, отрицание что Маша старше Лены'
        },
        {
            'step': 2,
            'type': 'resolution_step',
            'clause1_id': 1,
            'clause2_id': 2,
            'clause1': '¬Старше(x,y) ∨ ¬Старше(y,z) ∨ Старше(x,z)',
            'clause2': 'Старше(Маша, Катя)',
            'resolvent': '¬Старше(Катя,z) ∨ Старше(Маша,z)',
            'resolvent_id': 5,
            'unification': {'x': 'Маша', 'y': 'Катя'},
            'parents': [1, 2],
            'message': 'Применение транзитивности к Маша>Катя'
        },
        {
            'step': 3,
            'type': 'resolution_step',
            'clause1_id': 5,
            'clause2_id': 3,
            'clause1': '¬Старше(Катя,z) ∨ Старше(Маша,z)',
            'clause2': 'Старше(Катя, Лена)',
            'resolvent': 'Старше(Маша, Лена)',
            'resolvent_id': 6,
            'unification': {'z': 'Лена'},
            'parents': [5, 3],
            'message': 'Резолюции → Старше(Маша, Лена)'
        },
        {
            'step': 4,
            'type': 'contradiction_found',
            'clause1_id': 6,
            'clause2_id': 4,
            'clause1': 'Старше(Маша, Лена)',
            'clause2': '¬Старше(Маша, Лена)',
            'resolvent': '□',
            'message': 'Резолюция с ¬Старше(Маша, Лена) → Противоречие',
            'parents': [6, 4]
        }
    ]
    show_test(steps, success=True)


# ЗАПУСК
if __name__ == "__main__":
    print("\n" + " ТЕСТЫ ДЛЯ ProofExplainer — ОБЪЯСНЕНИЕ ДОКАЗАТЕЛЬСТВ ".center(80, "=") + "\n")

    test_socrates_mortal()
    test_john_liar()
    test_penguin_not_bird()
    test_contraposition_exam()
    test_only_masha()
    test_de_morgan_wizard()
    test_rain_accidents_chain()
    test_knights_liars_lancelot()
    test_transitivity_age()

    print("═" * 80)
    print("               ВСЕ ТЕСТЫ PROOFEXPLAINER ЗАВЕРШЕНЫ")
    print("═" * 80)