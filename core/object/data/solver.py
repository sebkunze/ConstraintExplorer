class Program:

    def __init__(self):

        self.states = []


    def __str__(self):

        return "%s(symbolic states: %s)" % (
            self.__class__.__name__, ','.join([str(s) for s in self.states]))


class SymbolicState:

    def __init__(self, state_id, conditions, effects, trace):

        self.state_id   = state_id
        self.conditions = conditions
        self.effects    = effects
        self.trace      = trace


    def __str__(self):

        return "%s(state_id: %s, conditions: [%s], effects: %s, trace: %s)" % (

            self.__class__.__name__, self.state_id, ','.join([str(c) for c in self.conditions]), ','.join([str(e) for e in self.effects]), ','.join([str(t) for t in self.trace]))


    def __eq__(self, other):

        if isinstance(other, SymbolicState):

            return self.state_id == other.state_id \
                   and self.conditions == other.conditions \
                   and self.trace == other.trace

        return NotImplemented


    def __hash__(self):

        return hash(self.state_id) + reduce(lambda x, y: x + hash(y), self.conditions, hash(''))


class Condition:

    def __init__(self, origin, typ, neg, com, cons):

        self.origin = origin
        self.typ    = typ
        self.neg    = neg
        self.com    = com
        self.cons   = cons



    def __str__(self):

        return "%s(origin: %s, typ: %s, negated: %s, combined: %s, constraints: [%s])" % (
            self.__class__.__name__, self.origin, self.typ, self.neg, self.com, ','.join([str(c) for c in self.cons]))


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

        self.var    = var
        self.op     = op
        self.val    = val


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