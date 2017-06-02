import re

from z3 import Bool, Int, And, Or, Implies, Not, Solver, sat

from core.object.data.test   import TestInfo, TestInstance
from core.utils              import logger


def analyse_program_states(program):
    create = []

    for state in program.states:
        # generate satisfying values.
        values = generate_satisfying_values([state])

        # collect test information.
        info = TestInfo("CREATE", state, [], values, [])

        # store test information.
        create.append(info)

    return create


def compare_program_states(to_be_tested_program, already_tested_program):
    create, skip, extend, adjust = [], [], [], []

    # iterate states to be tested.
    for to_be_tested_state in to_be_tested_program.states:

        logger.debug("Performing light-weight set-based analysis.%s", '')

        # perform a light-weight set-based analysis.
        syntactic_equivalent_states = find_syntactic_equivalent_states(to_be_tested_state, already_tested_program.states)

        if syntactic_equivalent_states:

            logger.info("Found %s syntactic equivalent state(s).", len(syntactic_equivalent_states))

            instance, values, _ = create_test_instance(to_be_tested_state, syntactic_equivalent_states)

            info = TestInfo("SYNTACTIC SKIP", to_be_tested_state, [instance], values, [])

            skip.append(info)

            continue

        syntactic_extending_states = find_syntactic_extending_states(to_be_tested_state, already_tested_program.states)

        if syntactic_extending_states:
            logger.info("Found %s syntactic extending state(s).", len(syntactic_extending_states))

            instance, values, behavioural_difference = create_test_instance(to_be_tested_state, syntactic_extending_states)

            info = TestInfo("SYNTACTIC EXTEND", to_be_tested_state, [instance], values, behavioural_difference)

            extend.append(info)

            continue

        logger.debug("Performing expensive z3-based analysis.%s",'')

        # perform a expensive z3-based analysis
        overlapping_states = find_overlapping_states(to_be_tested_state, already_tested_program.states)

        logger.info("Found %s overlapping state(s)", len(overlapping_states))

        if overlapping_states:

            semantic_equivalent_states = find_semantic_equivalent_states(to_be_tested_state, overlapping_states)

            if semantic_equivalent_states:

                logger.info("Found %s semantic equivalent state(s).", len(semantic_equivalent_states))

                instance, values, behavioural_difference = create_test_instance(to_be_tested_state, semantic_equivalent_states)

                info = TestInfo("SEMANTIC SKIP", to_be_tested_state, [instance], values, behavioural_difference)

                skip.append(info)

                continue

            logger.info("Found no semantic equivalent states.%s", '')

            instance, values, behavioural_difference = create_test_instance(to_be_tested_state, overlapping_states)

            info = TestInfo("ADJUST", to_be_tested_state, [instance], values, behavioural_difference)

            adjust.append(info)

            continue

        logger.info("Found state to create.%s", '')

        values = generate_satisfying_values([to_be_tested_state])

        info = TestInfo("CREATE", to_be_tested_state, [], values, [])

        create.append(info)

    return create, skip, extend, adjust


def create_test_instance(state_x, state_y):

    values = \
        generate_satisfying_values([state_x])

    trajected_state = \
        find_test_trajectory(state_x, state_y)

    trajected_values = \
        generate_satisfying_values([state_x] + [trajected_state])

    differential_values = \
        generate_differential_values(values, trajected_values)

    return TestInstance(trajected_state, []), trajected_values, differential_values


def find_test_trajectory(state_x, states_y):

    if states_y == []:
        return []

    # for now we just pick the very first state.
    return states_y[0]


def find_syntactic_equivalent_states(state_s, states_t):

    # find source state s in list of target states t.
    for state_t in states_t:
        if is_syntactic_equivalent_state(state_s, state_t):
            return [state_t]

    return []


def is_syntactic_equivalent_state(state_s, state_t):

    # compare state s' conditions and effects to those of state t.
    return is_syntactic_equivalent_condition(state_s.conditions, state_t.conditions) \
            and is_syntactic_equivalent_effect(state_s.effects, state_t.effects)


def is_syntactic_equivalent_condition(conditions_x, conditions_y):

    # perform set-based analysis.
    return set(conditions_x) == set(conditions_y)


def is_syntactic_equivalent_effect(effects_x, effects_y):

    # perform set-based analysis.
    return set(effects_x) == set(effects_y)


def find_semantic_equivalent_states(state_x, states_y):

    # find source state s in list of target states t.
    return [state_y for state_y in states_y if is_semantic_equivalent_state(state_x, state_y)]


def is_semantic_equivalent_state(state_x, state_y):

    # perform z3-based analysis.
    return is_semantic_equivalent_condition(state_x.conditions, state_y.conditions) \
           and is_semantic_equivalent_effect(state_x.effects, state_y.effects)


def is_semantic_equivalent_condition(conditions_x, conditions_y):

    s = Solver()

    # parse all conditions of state x.
    constraints_x = None
    for condition_x in conditions_x:

        # ignore 'axiom' and 'requires' definitions.
        # INFO: axioms and requires definition that are present in one state but not in the other will otherwise be flagged as non equivalent.
        if condition_x.typ != "ASSUME":
            continue

        constraint = to_z3_constraint(condition_x)

        if constraints_x is None:
            constraints_x = constraint

        else:
            constraints_x = And(constraint, constraints_x)

    # parse all conditions of state y.
    constraints_y = None
    for condition_y in conditions_y:

        # ignore 'axiom' and 'requires' definitions.
        # INFO: axioms and requires definition that are present in one state but not in the other will otherwise be flagged as non equivalent.
        if condition_y.typ != "ASSUME":
            continue

        constraint = to_z3_constraint(condition_y)

        if constraints_y is None:
            constraints_y = constraint

        else:
            constraints_y = And(constraint, constraints_y)

    #
    if constraints_x is None or constraints_y is None:
        return True

    # create scope for assertions.
    s.push()

    # check for differential behaviour.
    s.add(Not(Implies(constraints_x, constraints_y)))
    if s.check() == sat:
        return False

    # remove existing assertions.
    s.pop()

    # create scope for assertions.
    s.push()

    # check for differential behaviour.
    s.add(Not(Implies(constraints_y, constraints_x)))
    if s.check() == sat:
        return False

    # remove existing assertions.
    s.pop()

    return True


def is_semantic_equivalent_effect(effect_x, effect_y):

    # perform z3-based analysis.
    # TODO: Replace effect check with z3-based analysis.
    return is_syntactic_equivalent_effect(effect_x, effect_y)


def find_syntactic_extending_states(state_x, states_y):

    # find state x in list of states y.
    for state_y in states_y:
        if is_syntactic_extending_state(state_x, state_y):
            return [state_y]

    return []


def is_syntactic_extending_state(state_x, state_y):

    # TODO: Check if output is equivalent.


    origins_x = [strip_original_keyword(c.origin) for c in state_x.conditions if c.typ == "ASSUME"]
    origins_y = [strip_original_keyword(c.origin) for c in state_y.conditions if c.typ == "ASSUME"]

    # check for extending conditions in state y not in state x.
    if set(origins_x) < set(origins_y):
        return True

    # check for extending conditions in state x not in state y.
    if set(origins_y) < set(origins_x):
        return True

    return False


def strip_original_keyword(string):

    return re.sub(r'_original[\d]*', '', string)


def find_overlapping_states(state_s, states_t):

    # find source state s in list of target states t.
    return [state_t for state_t in states_t if is_overlapping_state_constraints(state_s, state_t)]


def is_overlapping_state_constraints(state_x, state_y):
    s = Solver()

    # create scope for assertions.
    s.push()

    # parse all conditions of state x.
    for condition in state_x.conditions:
        s.add(to_z3_constraint(condition))

    # parse all conditions of state y.
    for condition in state_y.conditions:
        s.add(to_z3_constraint(condition))

    # run z3 check.
    overlapping = True if s.check() == sat else False

    # remove existing assertions.
    s.pop()

    return overlapping


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

    if constraint is None:
        return True

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


def generate_satisfying_values(symbolic_states):
    s = Solver()

    # creating scope for assertions.
    s.push()

    # iterating symbolic states.
    for symbolic_state in symbolic_states:

        # iterating symbolic conditions.
        for condition in symbolic_state.conditions:
            s.add(to_z3_constraint(condition))

    # generate satisfying values.
    values = parse_satisfying_values(s.model()) if s.check() == sat else []

    # remove existing assertions.
    s.pop()

    return values


def generate_differential_values(values_x, values_y):

    return list(set(values_x) - set(values_y)) if list(set(values_y) - set(values_x)) == [] else list(set(values_y) - set(values_x))


def parse_satisfying_values(model):
    # FIXME: This is terrible! It seems like z3 inserts randomly \n characters when it is parsed to a string representation. Thus, we replace these characters and create a list.
    values = [v.strip() for v in (str(model).replace('\n', ''))[1:-1].split(',')]
    return values


def find_assertions(symbolic_state, overlapping_states):
    logger.info("Deriving missing assertions for symbolic state %s.", symbolic_state.id)

    assertions = dict()

    for overlapping_state in overlapping_states:
        assertions[overlapping_state.id] = set(symbolic_state.conditions) - set(overlapping_state.conditions)

    return assertions


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


def parse_to_z3_boolean_type(string):

    # parse true type.
    if string == "true" or string == "!false":
        typ = True

    # parse false type.
    elif string == "false" or string == "!true":
        typ = False

    # parse variable name, e.g., 'boolHeap[obj][field]
    else:
        typ = Bool(string)

    # TODO: Not best practise to return different types for a method.
    return typ


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

        s = c.split()
        if len(s) == 3:
            return True
        else:
            return False


def to_z3_integer_constraint(constraint):

    # parse left-hand side of constraint.
    left = parse_to_z3_integer_type(constraint.var)

    # parse right-hand side of constraint.
    right = parse_to_z3_integer_type(constraint.val)

    # combine information and build constraint.
    return parse_to_z3_constraint(left, constraint.op, right)


def parse_to_z3_integer_type(string):

    # parse digits, e.g., '1'
    if string.isdigit():
        typ = int(string)

    # parse arithmetic operations, e.g., '1 + intHeap[obj][field]'
    elif " + intHeap" in string:
        value, variable = string.split(" + ", 1)

        # check if value is a numerical value.
        if value.isdigit():
            typ = Int(variable) + int(value)

        else:
            typ = Int(string)

    # parse arithmetic operations, e.g., '1 - intHeap[obj][field]'
    elif " - intHeap" in string:
        value, variable = string.split(" - ", 1)

        # check if value is a numerical value.
        if value.isdigit():
            typ = Int(variable) - int(value)

        else:
            typ = Int(string)

    # parse variable name, e.g., 'intHeap[obj][field]
    else:
        typ = Int(string)

    # TODO: Not best practise to return different types for a method.
    return typ


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


def parse_to_z3_constraint(left, op, right):

    if op == "==" or op == "<==>":
        return left == right

    elif op == '!=':
        return left != right

    elif op == ">":
        return left > right

    elif op == "<":
        return left < right

    elif op == ">=":
        return left >= right

    elif op == "<=":
        return left <= right

    else:
        raise Exception("operator type %s not supported", op)


def z3_to_string(z3):
    return str(z3).replace('\n',' ')