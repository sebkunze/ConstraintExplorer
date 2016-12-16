from z3         import Int, And, Not
from symbooglix import ConstraintsIterator


class Program:
    def __init__(self, terminated_states = []):
        self.terminated_states = terminated_states

    def __repr__(self): # TODO: Insert new line operator!
        return "program variant with terminating states: " + str(self.terminated_states)

    def add_terminated_state(self, terminated_state):
        self.terminated_states.append(terminated_state)


class TerminatedState:
    def __init__(self, id = None, constraints = []):
        self.id          = id
        self.constraints = constraints

    def __repr__(self): # TODO: Insert new line operator!
        return "terminating state " + str(self.id) + " with constraints " + str(self.constraints)


class Constraint:
    # TODO: Figure out how to implement recursive data types!
    # def __init__(self, variable = None, operator = None, value = None):
    #     self.variable = variable
    #     self.operator = operator
    #     self.value    = value
    #
    # def __repr__(self): # TODO: Insert new line operator!
    #     return str(self.variable) + " " + str(self.operator) + " " + str(self.value)

    def __init__(self, z3constraint):
        self.z3constraint = z3constraint

    def __repr__(self):
        return str(self.z3constraint)

# TODO: Move to package utils!?!
def translate_to_program(terminated_symbooglix_states):
    p = Program([]) # TODO: Figure out why this destroyed everything!

    for s in terminated_symbooglix_states:
        id          = s.state_id
        constraints = []
        for c in ConstraintsIterator(s):
            # Trim the symbooglix overhead
            # TODO: Find more elegant solution!
            d = c['origin'][:-1].split()
            d = d[3:]

            e = []
            while True:             # do-while body
                var = d[0]
                op = d[1]
                val = d[2]

                y = gen_constraint(var, op, val)

                e.append(y)

                d = d[4:]  # TODO: Find a more appropriate name!
                if not len(d) > 0:  # do-while condition
                    break;

            j = None
            for f in e:
                if j is None:
                    j = f
                else:
                    j = And(j, f)

            constraints.append(j)
        t = TerminatedState(id, constraints)
        p.add_terminated_state(t)
    return p

def gen_constraint(var, op, val):
    if op == '==': # Do not use 'is' in favour of '=='
        if val.isdigit():
            return Int(var) == val
        else:
            return Int(var) == Int(val)
    else:
        if val.isdigit():
            return Not(Int(var) == val)
        else:
            return Not(Int(var) == Int(val))