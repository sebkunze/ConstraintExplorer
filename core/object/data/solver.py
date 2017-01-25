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
        return "\n %s\n id: %s\n constraints: %s" % (
            self.yaml_object_header(), self.id, self.constraints)

    def yaml_object_header(self):
        return "!!python/object:core.object.data.solver.SymbolicState"

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

    def is_equivalent_state(self, state): # TODO: Something seems to be wrong here!
        return True if set(self.constraints) == set(state.constraints) else False

class Constraint:
    """"""
    def z3(self):
        raise NotImplementedError("Should have implemented this")

class ComplexConstraint(Constraint):

    def __init__(self, neg, op, constraints):
        self.neg         = neg
        self.op          = op
        self.constraints = constraints

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
            # return Not(reduce(lambda x,y: And(x,y.z3()), self.constraints, []))
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

    z3 = None

    # if op is None and val is None:
    #     if var.startswith('!'):
    #         z3 = Bool(var[1:]) == False
    #     else:
    #         z3 = Bool(var) == True
    # else:
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

    z3 = None

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