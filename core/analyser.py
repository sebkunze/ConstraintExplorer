from z3 import Bool, Int, And, Implies, Not, Solver, sat

from core.object.data.test import Test
from core.utils            import logger


def analyse(programs):
    tests = []

    for program in programs:
        for state in program.states:
            _, values = gen_values(state)
            tests.append(Test(state, [], str(values).replace('\n', '')))

    return tests

def analyse_program_states(program_t, program_s):
    tests = []

    # target states to be tested.
    symbolic_states_t = program_t.states

    # source states tested.
    symbolic_states_s = program_s.states

    # find overlapping states.
    for symbolic_state_s in symbolic_states_s:

        logger.info("Searching for overlapping states of symbolic state %s.", symbolic_state_s.id)

        overlapping_symbolic_states = find_overlapping_states(symbolic_state_s, symbolic_states_t)

        logger.info("Found %i overlapping states.", len(overlapping_symbolic_states))

        if overlapping_symbolic_states:
            _, values = gen_values(symbolic_state_s)

            logger.info("Creating tests for symbolic state %s.", symbolic_state_s.id)

            tests.append(Test(symbolic_state_s, overlapping_symbolic_states, str(values).replace('\n','')))

    return tests


def find_overlapping_states(state_s, states_t):
    # find source state s in list of target states t.
    return [state_t for state_t in states_t if is_overlapping_state(state_s, state_t) and not is_equivalent_state(state_s, state_t)]


def is_overlapping_state(state_s, state_t):
    s = Solver()

    for condition in state_s.conditions:
        s.add(x_z3(condition))

    for condition in state_t.conditions:
        s.add(x_z3(condition))

    return True if s.check() == sat else False


def find_equivalent_states(state_s, states_t):
    # find source state s in list of target states t.
    return [state_t for state_t in states_t if is_equivalent_state(state_s, state_t)]


def is_equivalent_state(state_s, state_t):
    return True if set(state_s.conditions) == set(state_t.conditions) else False

def x_z3(condition): # TODO: Change method name!
    constraints = map(lambda c: to_z3(c), condition.cons)

    x = None
    for c in constraints:
        if x is None:
            x = c
        else:
            x = And(x, c)

    if condition.neg:
        x = Not(x)

    return x

def to_z3(constraint): # TODO: Change method name!
    if is_boolean_constraint(constraint.var) \
            or is_boolean_constraint(constraint.val):
        return to_boolean_constraint(constraint)
    elif is_integer_constraint(constraint.var) \
            or is_integer_constraint(constraint.val):
        return to_integer_constraint(constraint)
    else:
        raise Exception("type not supported.")

def gen_values(symbolic_state):
    s = Solver()

    logger.info("Generating values for symbolic state %s.", symbolic_state.id)

    for condition in symbolic_state.conditions:
        s.add(x_z3(condition))

    if s.check() == sat:
        return True, s.model()
    else:
        s.pop()
        return False, None


def is_boolean_variable(b):
    return b[0] is 'b'


def is_boolean_value(b):
    return b == 'true' or b == 'false'


def is_boolean_constraint(s):
    # handle parenthesis.
    s.replace('(','')
    s.replace(')','')

    # handle negating operator.
    if s.startswith('!'):
        s = s[1:]

    return s[0] is 'b'


def to_boolean_constraint(constraint):
    var = constraint.var
    op  = constraint.op
    val = constraint.val

    logger.debug("Generating z3 boolean for %s", constraint)

    if op == '==' or op == '<==>':
        # variable and value
        # variable and variable
        # value and variable
        if val == 'true' or val == '!false':
            z3 = Bool(var) == True
        else:
            z3 = Bool(var) == False
    else:
        if val == 'true' or val == '!false':
            z3 = Bool(var) != True
        else:
            z3 = Bool(var) != False

    logger.debug("Generated z3 boolean constraint: %s", str(z3).replace('\n',' '))

    return z3


def is_integer_variable(i):
    return i[0] is 'i'


def is_integer_value(i):
    return not i.isdigit()


def is_integer_constraint(s):
    # handle parenthesis.
    s.replace('(', '')
    s.replace(')', '')

    # handle negating operator.
    if s.startswith('!'):
        s = s[1:]

    return s[0] is 'i'


def to_integer_constraint(constraint):
    var = constraint.var
    op  = constraint.op
    val = constraint.val

    logger.info("Generating z3 integer constraints for %s", constraint)

    if op == '==' or op == '<==>':
        # variable and value
        if (not var.isdigit()) and val.isdigit():
            z3 = Int(var) == int(val)
        # variable and variable
        elif (not var.isdigit()) and (not val.isdigit()):
            z3 = Int(var) == Int(val)
        # value and variable
        elif var.isdigit() and (not val.isdigit()):
            z3 = int(var) == Int(val)
        # otherwise
        else:
            raise Exception("cannot parse constraint!")
    else:
        # variable and value
        if (not var.isdigit()) and val.isdigit():
            z3 = Int(var) != int(val)
        # variable and variable
        elif (not var.isdigit()) and (not val.isdigit()):
            z3 = Int(var) != Int(val)
        # value and variable
        elif var.isdigit() and (not val.isdigit()):
            z3 = int(var) != Int(val)
        # otherwise
        else:
            raise Exception("cannot parse constraint!")

    logger.debug("Generated z3 integer constraint: %s", str(z3).replace('\n',' '))

    return z3