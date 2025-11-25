from copy import deepcopy
from collections import deque

# -------------------------
# Классы литералов и клауз
# -------------------------
class Literal:
    def __init__(self, predicate, args, negated=False):
        self.predicate = predicate
        self.args = args
        self.negated = negated

    def complement(self):
        return Literal(self.predicate, self.args, not self.negated)

    def __eq__(self, other):
        return (self.predicate, tuple(self.args), self.negated) == (other.predicate, tuple(other.args), other.negated)

    def __hash__(self):
        return hash((self.predicate, tuple(self.args), self.negated))

    def __repr__(self):
        return ("¬" if self.negated else "") + f"{self.predicate}({', '.join(map(str, self.args))})"


class Clause:
    def __init__(self, literals, parents=None):
        self.literals = set(literals)
        self.parents = parents if parents else ()  # tuple(c1, c2)

    def __repr__(self):
        return " ∨ ".join(map(str, self.literals))

    def __eq__(self, other):
        return self.literals == other.literals

    def __hash__(self):
        return hash(frozenset(self.literals))


# -------------------------
# Унификация термов
# -------------------------
def is_variable(t):
    return isinstance(t, str) and t[0].islower()

def unify_var(var, x, subst):
    if var in subst:
        return unify(subst[var], x, subst)
    elif is_variable(x) and x in subst:
        return unify(var, subst[x], subst)
    else:
        new_subst = subst.copy()
        new_subst[var] = x
        return new_subst

def unify(t1, t2, subst={}):
    if subst is None:
        return None
    if t1 == t2:
        return subst
    if is_variable(t1):
        return unify_var(t1, t2, subst)
    if is_variable(t2):
        return unify_var(t2, t1, subst)
    if isinstance(t1, tuple) and isinstance(t2, tuple) and t1[0] == t2[0]:
        for a1, a2 in zip(t1[1], t2[1]):
            subst = unify(a1, a2, subst)
            if subst is None:
                return None
        return subst
    return None

def unify_literals(l1, l2):
    if l1.predicate != l2.predicate or l1.negated == l2.negated:
        return None
    subst = {}
    for a1, a2 in zip(l1.args, l2.args):
        subst = unify(a1, a2, subst)
        if subst is None:
            return None
    return subst

def apply_subst(literal, subst):
    new_args = []
    for arg in literal.args:
        while is_variable(arg) and arg in subst:
            arg = subst[arg]
        new_args.append(arg)
    return Literal(literal.predicate, new_args, literal.negated)


# -------------------------
# Резолюция двух клауз
# -------------------------
def resolve(c1, c2):
    resolvents = []
    for l1 in c1.literals:
        for l2 in c2.literals:
            subst = unify_literals(l1, l2)
            if subst is not None:
                new_literals = {apply_subst(lit, subst) for lit in c1.literals.union(c2.literals) - {l1, l2}}
                # фильтруем тавтологии
                if not any(lit.complement() in new_literals for lit in new_literals):
                    resolvents.append(Clause(new_literals, parents=(c1, c2)))
    return resolvents


# -------------------------
# Алгоритм резолюции с логом
# -------------------------
def resolution(clauses):
    passive = deque(clauses)
    active = set()
    seen = set()  # чтобы не добавлять одинаковые клаузи
    step = 1

    while passive:
        c = passive.popleft()
        active.add(c)
        seen.add(c)

        for a in list(active):
            # запрещаем резольвить родителя с потомком
            if c in a.parents or a in c.parents:
                continue
            for resolvent in resolve(c, a):
                print(f"Шаг {step}: {c} резольвента {a} => {resolvent}")
                step += 1

                if not resolvent.literals:
                    print("Пустая клауза найдена — доказательство!")
                    return True

                if resolvent not in seen:
                    passive.append(resolvent)
                    seen.add(resolvent)

    print("Доказательство не найдено")
    return False


# -------------------------
# Пример использования
# -------------------------
if __name__ == "__main__":
    # Формула в виде массива клауз
    c1 = Clause([Literal("P", ["x"], True), Literal("Q", ["x"])])
    c2 = Clause([Literal("P", ["x"])])
    c3 = Clause([Literal("Q", ["a"], True)])


    c1 = Clause([Literal("P", ["x"], True), Literal("Q", ["x"])])
    c2 = Clause([Literal("P", ["x"])])
    c3 = Clause([Literal("Q", ["a"], True)])
    

    clauses = [c1, c2, c3]
    resolution(clauses)
