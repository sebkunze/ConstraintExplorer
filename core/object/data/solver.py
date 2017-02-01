from z3 import Bool, Int, And, Implies, Not, Solver, sat

from core.utils import logger

class Program:
    """class representing an analysed program"""
    def __init__(self, symbolic_states = []):
        self.symbolic_states = symbolic_states

    def __repr__(self):
        return "%s(terminated_states: %s)" % (
            self.__class__.__name__, self.symbolic_states)

    def __str__(self):
        return "%s(terminated_states: %s)" % (
            self.__class__.__name__, self.symbolic_states)

    def add_symbolic_state(self, symbolic_state):
        self.symbolic_states.append(symbolic_state)


class SymbolicState:
    """class representing a symbolic state"""
    def __init__(self, id = None, constraints = []):
        self.id          = id
        self.constraints = constraints

    def __str__(self):
        return "%s(id: %s, constraints: %s)" % (
            self.__class__.__name__, self.id, self.constraints)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def find_overlapping_states(self, states):
        return [s for s in states if self.is_overlapping_state(s) and not self.is_equivalent_state(s)]

    def is_overlapping_state(self, state):
        s = Solver()

        for constraint in self.constraints:
            s.add(constraint.z3())

        for constraint in state.constraints:
            s.add(constraint.z3())

        return True if s.check() == sat else False

    def find_equivalent_states(self, states):
        return [s for s in states if self.is_equivalent_state(s)]

    def is_equivalent_state(self, state):
        return True if set(self.constraints) == set(state.constraints) else False

    def gen_values(self):
        s = Solver()

        logger.info("Generating values for symbolic state %s.", self.id)

        for constraint in self.constraints:
            s.add(constraint.z3())

        if s.check() == sat:
            return True,  s.model()
        else:
            s.pop()
            return False, None

class Constraint:
    """"""
    def z3(self):
        raise NotImplementedError("abstract method call")

class ComplexConstraint(Constraint):

    def __init__(self, neg, op, constraints):
        self.neg         = neg
        self.op          = op
        self.constraints = constraints


    def __eq__(self, other):
        if isinstance(other, ComplexConstraint):
            return self.neg == other.neg \
                   and self.op == other.op \
                   and self.constraints == other.constraints

        return NotImplemented

    def __hash__(self):
        return hash(self.neg) + hash(self.op) + reduce(lambda x,y: x + hash(y), self.constraints, hash(''))

    def __str__(self):
        if self.neg:
            return "!(%s)" \
                   % reduce(lambda x,y: str(x) + ' && ' + str(y), self.constraints)
        else:
            return "%s" \
                   % reduce(lambda x,y: str(x) + ' && ' + str(y), self.constraints)

    def z3(self):
        if self.neg:
            x = None
            for c in self.constraints:
                if x is None:
                    x = c.z3()
                else:
                    x = And(x, c.z3())

            return Not(x)
        else:
            x = None
            for c in self.constraints:
                if x is None:
                    x = c.z3()
                else:
                    x = And(x, c.z3())

            return x

class SimpleConstraint(Constraint):

    def __init__(self, neg, var, op, val):
        self.neg = neg
        self.var = var
        self.op  = op
        self.val = val

    def __eq__(self, other):
        if isinstance(other, SimpleConstraint):
            return self.neg == other.neg \
                   and self.var == other.var \
                   and self.op == other.op \
                   and self.val == other.val

        return NotImplemented

    def __hash__(self):
        return hash(self.neg) + hash(self.var) + hash(self.op) + hash(self.val)

    def __str__(self):
        if self.neg:
            if self.op is None and self.val is None:
                return "!%s" \
                       % self.var
            else:
                return "!(%s %s %s)" \
                       % (self.var, self.op, self.val)
        else:
            if self.op is None and self.val is None:
                return "%s" \
                       % self.var
            else:
                return "%s %s %s" \
                       % (self.var, self.op, self.val)

    def toggle(self):
        self.neg = not self.neg

    def z3(self):
        if   is_boolean_constraint(self):
            return to_boolean_constraint(self)
        elif is_integer_constraint(self):
            return to_integer_constraint(self)

def is_boolean_constraint(constraint):
    var = constraint.var

    # handle parenthesis.
    var.replace('(','')
    var.replace(')','')

    # handle negating operator.
    if var.startswith('!'):
        var = var[1:]

    is_boolean_constraint = var[0] is 'b'

    return is_boolean_constraint

def to_boolean_constraint(constraint):
    logger.debug("Generating z3 boolean for %s", constraint)
    neg = constraint.neg
    var = constraint.var
    op  = constraint.op
    val = constraint.val

    if not var.startswith('!'):
        if op == '==' or op == '<==>':
            if val == 'true' or val == '!false':
                z3 = Bool(var) == True
            else:
                z3 = Bool(var) == False
        else:
            if val == 'true' or val == '!false':
                z3 = Bool(var) != True
            else:
                z3 = Bool(var) != False
    else:
        var = var[1:]
        if op == '==' or op == '<==>':
            if val == 'true' or val == '!false':
                z3 = Bool(var) != True
            else:
                z3 = Bool(var) != False
        else:
            if val == 'true' or val == '!false':
                z3 = Bool(var) == True
            else:
                z3 = Bool(var) == False

    if neg:
        z3 = Not(z3)

    logger.debug("-> %s", str(z3).replace('\n',' '))

    return z3

def is_integer_constraint(constraint):
    var = constraint.var

    # handle parenthesis.
    var.replace('(', '')
    var.replace(')', '')

    # handle negating operator.
    if var.startswith('!'):
        var = var[1:]

    is_integer_constraint = var[0] is 'i'

    return is_integer_constraint

def to_integer_constraint(constraint):
    logger.debug("Generating z3 integer constraints for %s", constraint)
    neg = constraint.neg
    var = constraint.var
    op  = constraint.op
    val = constraint.val

    if not var.startswith('!'):
        if op == '==' or op == '<==>':
            if val.isdigit():
                z3 = Int(var) == int(val)
            else:
                z3 = Int(var) == Int(val)
        else:
            if val.isdigit():
                z3 = Int(var) != int(val)
            else:
                z3 = Int(var) != Int(val)
    else:
        if op == '==' or op == '<==>':
            if val.isdigit():
                z3 = Int(var) != int(val)
            else:
                z3 = Int(var) != Int(val)
        else:
            if val.isdigit():
                z3 = Int(var) == int(val)
            else:
                z3 = Int(var) == Int(val)

    if neg:
        z3 = Not(z3)

    logger.debug("-> %s", str(z3).replace('\n',' '))

    return z3