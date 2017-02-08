class Program:

    def __init__(self):
        self.states = []

    def __str__(self):
        return "%s(states: %s)" % (
            self.__class__.__name__, self.states)


class SymbolicState:

    def __init__(self, id, conditions, trace):
        self.id         = id
        self.conditions = conditions
        self.trace      = trace

    def __str__(self):
        return "%s(id: %s, conditions: %s, trace: %s)" % (
            self.__class__.__name__, self.id, reduce(lambda x, y: x + str(y), self.conditions, ''), self.trace)

    def __eq__(self, other):
        if isinstance(other, SymbolicState):
            return self.id == other.id \
                   and self.conditions == other.conditions \
                   and self.trace == other.trace

        return NotImplemented

    def __hash__(self):
        return hash(self.id) + reduce(lambda x, y: x + hash(y), self.conditions, hash(''))


class Condition:

    def __init__(self, neg, com, cons):
        self.neg  = neg
        self.com  = com
        self.cons = cons

    def __str__(self):
        return "%s(neg: %s, com: %s, cons: %s)" % (
            self.__class__.__name__, self.neg, self.com, '[' + reduce(lambda x, y: x + ', ' + str(y), self.cons, '')[2:] + ']')

    def __eq__(self, other):
        if isinstance(other, Condition):
            return self.neg == other.neg \
                   and self.com == other.com \
                   and self.cons == other.cons

        return NotImplemented

    def __hash__(self):
        return hash(self.neg) + hash(self.com) + reduce(lambda x, y: x + hash(y), self.cons, hash(''))


class Constraint:

    def __init__(self, var, op, val):
        self.var = var
        self.op  = op
        self.val = val

    def __str__(self):
        return "%s(var: %s, op: %s, val: %s)" % (
            self.__class__.__name__, self.var, self.op, self.val)

    def __eq__(self, other):
        if isinstance(other, Constraint):
            return self.var == other.var \
                   and self.op == other.op \
                   and self.val == other.val

        return NotImplemented

    def __hash__(self):
        return hash(self.var) + hash(self.op) + hash(self.val)