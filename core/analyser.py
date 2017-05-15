from z3 import Bool, Int, And, Or, Implies, Not, Solver, sat

from core.object.data.test import TestInfo, TestInstance
from core.utils            import logger, report


def analyse_program_states(program):
    tests = []

    for state in program.states:
        # generate satisfying values.
        values = gen_satisfying_values_for_state(state)

        # store test information.
        tests.append(TestInfo("CREATE", state, [], values))

        report.to_be_created_test()

    return tests


def compare_program_states(to_be_tested_program, already_tested_program):
    states = []

    for to_be_tested_state in to_be_tested_program.states:
        logger.info("Inspecting symbolic state %s", to_be_tested_state.identifier)

        equivalent_states = \
            find_equivalent_states(to_be_tested_state, already_tested_program.states)

        if equivalent_states:
            logger.debug("Found %s equivalent state(s) to skip.", len(equivalent_states))

            test_instances = \
                gen_test_instances(to_be_tested_state, already_tested_program.states)

            info = TestInfo("SKIP", to_be_tested_state, test_instances, [])

            report.to_be_skipped_test()

            states.append(info)
        else:
            test_instances = \
                gen_test_instances(to_be_tested_state, already_tested_program.states)

            logger.debug("Found %s test instance(s) to reuse.", len(test_instances))

            values = \
                gen_satisfying_values_for_state(to_be_tested_state)

            if test_instances:
                trajectory = "ADJUST"

                report.to_be_adjusted_test()

            else:
                trajectory = "CREATE"

                report.to_be_created_test()

            info = \
                TestInfo(trajectory, to_be_tested_state, test_instances, values)

            states.append(info)

    return states


def gen_test_instances(to_be_tested_state, already_tested_states):
    overlapping_states \
        = find_overlapping_states(to_be_tested_state, already_tested_states)

    instances = []

    # for overlapping_state in overlapping_states:
    #     values = gen_satisfying_values_for_states([to_be_tested_state] + [overlapping_state])
    #
    #     instances.append(TestInstance(overlapping_state, values))

    if overlapping_states:
        overlapping_state = overlapping_states[0]

        values = gen_satisfying_values_for_states([to_be_tested_state] + [overlapping_state])

        instances.append(TestInstance(overlapping_state, values))

    return instances


def find_overlapping_states(to_be_tested_state, already_tested_states):
    # find source state s in list of target states t.
    return [already_tested_state for already_tested_state in already_tested_states if is_overlapping_state(to_be_tested_state, already_tested_state)]


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
    # compare state s' conditions and effects to those of state t.
    return set(state_s.conditions) == set(state_t.conditions) \
            and set(state_s.effects) == set(state_t.effects)


def to_z3_constraint(condition): # TODO: Change method name!
    constraints = map(lambda c: parse_to_z3_object(c), condition.cons)

    x = None
    for c in constraints:
        if x is None:
            x = c
        elif condition.com == "&&":
                x = And(x, c)
        elif condition.com == "||":
                x = Or(x, c)
        else:
            logger.error("Missing logical combinator in condition: %s", condition)

    if condition.neg:
        x = Not(x)

    return x


def parse_to_z3_object(constraint):

    # unpack variables, e.g., 'heap[this][MyClass.field]' or 'someMethod.variable'
    var = unpack_variable_name(constraint.var)
    val = unpack_variable_name(constraint.val)

    if is_boolean_constraint(var) \
            or is_boolean_constraint(val):

        return to_z3_boolean_constraint(constraint)

    elif is_integer_constraint(var) \
            or is_integer_constraint(val):

        return to_z3_integer_constraint(constraint)

    elif is_object_constraint(var) \
            or is_object_constraint(constraint.val):

        return to_z3_object_constraint(constraint)

    else:
        logger.error("Type of constraint not supported: %s", constraint)
        raise Exception("type not supported.")


def unpack_variable_name(string):

    # ignore fields.
    if string.startswith("boolHeap") \
        or string.startswith("intHeap") \
        or string.startswith("objHeap"):

        return string


    return string.rsplit(".",1)[-1]


def gen_satisfying_values_for_state(symbolic_state):
    s = Solver()

    logger.info("Generating satisfying values for symbolic states %s.", symbolic_state.identifier)

    for condition in symbolic_state.conditions:
        s.add(to_z3_constraint(condition))

    values = []

    if s.check() == sat:
        values = model_to_list(s.model())

    return values


def gen_satisfying_values_for_states(symbolic_states):
    s = Solver()

    logger.info("Generating satisfying values for symbolic states %s.", reduce(lambda x,y: x + str(y) + ", ", [state.identifier for state in symbolic_states], ""))

    for symbolic_state in symbolic_states:
        for condition in symbolic_state.conditions:
            s.add(to_z3_constraint(condition))

    values = []

    if s.check() == sat:
        values = model_to_list(s.model())

    return values


def model_to_list(model):
    # FIXME: This is terrible! It seems like z3 inserts randomly \n characters when it is parsed to a string representation. Thus, we replace these characters and create a list.
    values = [v.strip() for v in (str(model).replace('\n', ''))[1:-1].split(',')]
    return values


def find_assertions(symbolic_state, overlapping_states):
    logger.info("Deriving missing assertions for symbolic state %s.", symbolic_state.id)

    assertions = dict()

    for overlapping_state in overlapping_states:
        assertions[overlapping_state.id] = set(symbolic_state.conditions) - set(overlapping_state.conditions)

    return assertions


# def is_boolean_variable(b):
#     return b[0] is 'b'
#
#
# def is_boolean_value(b):
#     return b == 'true' or b == 'false'


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


# def is_integer_variable(i):
#     return i[0] is 'i'
#
#
# def is_integer_value(i):
#     return not i.isdigit()


def is_integer_constraint(c):
    # handle parenthesis.
    c.replace('(', '')
    c.replace(')', '')

    # handle negating operator.
    if c.startswith('!'):
        c = c[1:]

    if c.startswith("i"):
        return True
    elif "$size" in c:
        return True
    elif c.isdigit():
        return False
    else:
        # some symbooglix constraint refer to operations like '1 + intHeap[obj][field] > 0'

        logger.debug("Breaking down constraint %s.", c)

        s = c.split()
        if len(s) == 3:
            return True
        else:
            return False


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

def is_object_constraint(s):
    # handle parenthesis.
    s.replace('(','')
    s.replace(')','')

    # handle negating operator.
    if s.startswith('!'):
        s = s[1:]

    return s[0] is 'o'

def to_z3_object_constraint(constraint):
    var = constraint.var
    op  = constraint.op
    val = constraint.val

    logger.info("Generating z3 integer constraints for %s", constraint)

    if op == '==':
        if var == "null" and val != "null":
            z3 = Int(var) == int(0)
        elif var != "null" and val == "null":
            z3 = int(0) == Int(val)
        elif var != "null" and val != "null":
            z3 = Int(var) == Int(val)
        else:
            raise Exception("cannot parse constraint!")
    elif op == '!=':
        if var == "null" and val != "null":
            z3 = Int(var) != int(0)
        elif var != "null" and val == "null":
            z3 = int(0) != Int(val)
        elif var != "null" and val != "null":
            z3 = Int(var) != Int(val)
        else:
            raise Exception("cannot parse constraint!")
    else:
        raise Exception("cannot parse constraint!")

    logger.debug("Generated z3 integer constraint: %s", str(z3).replace('\n',' '))

    return z3


def z3_to_string(z3):
    return str(z3).replace('\n',' ')