from z3 import Bool, Int, And, Implies, Not, Solver, sat

from core.object.data.test import TestInfo, TestInstance, AssertionType
from core.utils            import logger


def analyse_program_states(program):
    tests = []

    for state in program.states:
        # generate satisfying values.
        values = gen_satisfying_values(state)

        # store test information.
        tests.append(TestInfo(state, [], values))

    return tests


def compare_program_states(to_be_tested_program, already_tested_program):
    tests = []

    for to_be_tested_state in to_be_tested_program.states:

        logger.info("Inspecting symbolic state %s", to_be_tested_state.id)

        equivalent_states = \
            find_equivalent_states(to_be_tested_state, already_tested_program.states)

        if equivalent_states:
            logger.debug("Found %s equivalent state(s).", len(equivalent_states))

            continue
        else:
            logger.debug("Found no equivalent states.%s", '')

            test_instances = \
                gen_test_instances(to_be_tested_state, already_tested_program.states)

            logger.debug("Found %s test instance(s).", len(test_instances))

            values = \
                gen_satisfying_values(to_be_tested_state)

            logger.debug("Generated list of satisfying values.%s", '')

            info = \
                TestInfo(to_be_tested_state, test_instances, values)

            tests.append(info)

    return tests


def gen_test_instances(to_be_tested_state, already_tested_states):
    overlapping_states \
        = find_overlapping_states(to_be_tested_state, already_tested_states)

    instances = []
    for overlapping_state in overlapping_states:
        assertion_conditions, assertion_type = gen_assertions(to_be_tested_state, overlapping_state)
        instances.append(TestInstance(assertion_conditions, assertion_type, overlapping_state))

    return instances


def gen_assertions(to_be_tested_state, overlapping_state):
    assertion_coditions = list(set(to_be_tested_state.conditions) - set(overlapping_state.conditions))

    if len(assertion_coditions) > 0:
        return assertion_coditions, 'ADD' # AssertionType.ADD

    assertion_coditions= list(set(overlapping_state.conditions) - set(to_be_tested_state.conditions))

    if len(assertion_coditions) > 0:
        return assertion_coditions, 'REMOVE' # AssertionType.REMOVE

    return [], 'NONE' # AssertionType.NONE


def find_overlapping_states(to_be_tested_state, already_tested_states):
    # find source state s in list of target states t.
    return [already_tested_state for already_tested_state in already_tested_states if is_overlapping_state(to_be_tested_state, already_tested_state)]

    # overlapping_states = []
    #
    # for already_tested_state in already_tested_states:
    #     if not is_overlapping_state(to_be_tested_state, already_tested_state):
    #         continue
    #
    #     already_tested_state.assertions = list(set(to_be_tested_state.conditions) - set(already_tested_state.conditions))
    #
    #     overlapping_states.append(already_tested_state)
    #
    # return overlapping_states


def is_overlapping_state(state_x, state_y):
    s = Solver()

    for condition in state_x.conditions:
        s.add(to_z3_constraint(condition))

    for condition in state_y.conditions:
        s.add(to_z3_constraint(condition))

    return True if s.check() == sat else False


def find_equivalent_states(state_s, states_t):
    # find source state s in list of target states t.
    return [state_t for state_t in states_t if is_equivalent_state(state_s, state_t)]


def is_equivalent_state(state_s, state_t):
    return True if set(state_s.conditions) == set(state_t.conditions) else False


def to_z3_constraint(condition): # TODO: Change method name!
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
        return to_z3_boolean_constraint(constraint)
    elif is_integer_constraint(constraint.var) \
            or is_integer_constraint(constraint.val):
        return to_z3_integer_constraint(constraint)
    else:
        raise Exception("type not supported.")


def gen_satisfying_values(symbolic_state):
    s = Solver()

    logger.info("Generating satisfying values for symbolic state %s.", symbolic_state.id)

    for condition in symbolic_state.conditions:
        s.add(to_z3_constraint(condition))

    model = ''

    if s.check() == sat:
        model = str(s.model()).replace('\n', '')

    return model


def find_assertions(symbolic_state, overlapping_states):
    logger.info("Deriving missing assertions for symbolic state %s.", symbolic_state.id)

    assertions = dict()

    for overlapping_state in overlapping_states:
        assertions[overlapping_state.id] = set(symbolic_state.conditions) - set(overlapping_state.conditions)

    return assertions


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


def to_z3_boolean_constraint(constraint):
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


def to_z3_integer_constraint(constraint):
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
    elif op == '!=':
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
    elif op == ">":
        # variable and value
        if (not var.isdigit()) and val.isdigit():
            z3 = Int(var) > int(val)
        # variable and variable
        elif (not var.isdigit()) and (not val.isdigit()):
            z3 = Int(var) > Int(val)
        # value and variable
        elif var.isdigit() and (not val.isdigit()):
            z3 = int(var) > Int(val)
        # otherwise
        else:
            raise Exception("cannot parse constraint!")
    elif op == "<":
        # variable and value
        if (not var.isdigit()) and val.isdigit():
            z3 = Int(var) < int(val)
        # variable and variable
        elif (not var.isdigit()) and (not val.isdigit()):
            z3 = Int(var) < Int(val)
        # value and variable
        elif var.isdigit() and (not val.isdigit()):
            z3 = int(var) < Int(val)
        # otherwise
        else:
            raise Exception("cannot parse constraint!")
    elif op == ">=":
        # variable and value
        if (not var.isdigit()) and val.isdigit():
            z3 = Int(var) >= int(val)
        # variable and variable
        elif (not var.isdigit()) and (not val.isdigit()):
            z3 = Int(var) >= Int(val)
        # value and variable
        elif var.isdigit() and (not val.isdigit()):
            z3 = int(var) >= Int(val)
        # otherwise
        else:
            raise Exception("cannot parse constraint!")
    elif op == "<=":
        # variable and value
        if (not var.isdigit()) and val.isdigit():
            z3 = Int(var) <= int(val)
        # variable and variable
        elif (not var.isdigit()) and (not val.isdigit()):
            z3 = Int(var) <= Int(val)
        # value and variable
        elif var.isdigit() and (not val.isdigit()):
            z3 = int(var) <= Int(val)
        # otherwise
        else:
            raise Exception("cannot parse constraint!")

    logger.debug("Generated z3 integer constraint: %s", str(z3).replace('\n',' '))

    return z3


def z3_to_string(z3):
    return str(z3).replace('\n',' ')