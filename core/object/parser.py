import re

from core.object.data.solver     import Program, SymbolicState, Condition, Constraint
from core.object.data.symbooglix import SymbooglixConstraintIterator
from core.utils                  import logger

def to_program(terminated_symbooglix_states):
    program = Program()

    # iterate terminated states of symbolically executed program
    for symbooglix_state in terminated_symbooglix_states:

        # check if state is failing termination type.
        if is_failing_termination_type(symbooglix_state):
            continue

        logger.info("Extracting state's id.%s", '')

        # retrieve id.
        state_id = to_id(symbooglix_state)

        logger.info("Extracting state's conditions.%s", '')

        # retrieve conditions.
        conditions = to_conditions(symbooglix_state)

        logger.info("Looking up state's effects.%s",'')

        # retrieve effects.
        effects = to_effects(symbooglix_state)

        logger.info("Extracting state's trace.%s", '')

        # retrieve trace.
        trace = to_trace(symbooglix_state)

        logger.info("Combining state's information.%s", '')

        # create symbolic state
        state = SymbolicState(state_id, conditions, effects, trace)

        logger.info("Adding state's information to program.%s", '')

        # add identified state.
        program.states.append(state)

    return program


def to_id(symbooglix_state):
    return symbooglix_state.state_id


def is_failing_termination_type(symbooglix_state):

    # retrieve termination type information
    termination_type = symbooglix_state.status['termination_type']

    # check if is not failing termination type
    if termination_type == "Symbooglix.TerminatedWithoutError":
        return False

    return True


def to_conditions(symbooglix_state):

    # list of conditions.
    conditions = []

    # iterate constraints of terminated state
    for symbooglix_constraint in SymbooglixConstraintIterator(symbooglix_state):

        # retrieve information in 'origin'
        origin = symbooglix_constraint['origin']

        # match type of expression.
        if origin.startswith("[Axiom]"):
            typ = "AXIOM"

        elif origin.startswith("[Cmd]"):
            typ = "ASSUME"

        elif origin.startswith("[Requires]"):
            typ = "REQUIRES"

        else:
            typ = "Unknown"

        # retrieve information in 'expr'.
        constraint = symbooglix_constraint['expr']

        if constraint == 'true':
            continue

        logger.info("> Analysing symbooglix constraint: %s", constraint)

        # split symbooglix constraints into its nested parts
        has_negation_operator, has_logic_operator, symbooglix_nested_constraints = \
            split_complex_constraint(constraint)

        # list of nested constraints.
        nested_constraints = []

        # iterate nested parts of constraint.
        for symbooglix_nested_constraint in symbooglix_nested_constraints:
            # TODO: Splitting nested constraints seems to have side-effect in some cases; needs some further investigation!
            if symbooglix_nested_constraint == '':
                continue

            # strip whitespaces on the both side.
            symbooglix_nested_constraint = symbooglix_nested_constraint.strip()

            # remove parentheses on both sides.
            if symbooglix_nested_constraint.startswith('('):  # TODO: Add check whether it has closing bracket!
                symbooglix_nested_constraint = symbooglix_constraint[1:-1]

            logger.debug(">> Parsing symbooglix nested constraint: %s", symbooglix_nested_constraint)

            # parse to nested constraint.
            nested_constraint = to_constraint(symbooglix_nested_constraint)

            logger.debug(">> Parsed to constraint: %s", nested_constraint)

            # add to nested constraint.
            nested_constraints.append(nested_constraint)

        # generate condition.
        condition = Condition(origin, typ, has_negation_operator, has_logic_operator, nested_constraints)

        logger.info("> Generated condition: %s", condition)

        # add to collected conditions.
        conditions.append(condition)

    return conditions


def split_complex_constraint(expr):
    logger.debug(">> Splitting complex symbooglix constraint: %s", expr)

    has_negation_operator = False;

    if expr.startswith('!('):
        has_negation_operator = True

        expr = expr[2:-1]
    elif expr.startswith('!'):
        has_negation_operator = True

        expr = expr[1:]

    logger.debug(">>> Complex symbooglix constraint has negation: %s", has_negation_operator)

    has_logic_operator = None

    if "&&" in expr:
        delimiters = "&&"
        pattern = '|'.join(map(re.escape, delimiters))
        constraints = re.split(pattern, expr)

        has_logic_operator = "&&"

        logger.debug(">>> Complex symbooglix constraint has && operator: %s", True)

    if "||" in expr:
        delimiters = "||"
        pattern = '|'.join(map(re.escape, delimiters))
        constraints = re.split(pattern, expr)

        has_logic_operator = "||"

        logger.debug(">>> Complex symbooglix constraint has || operator: %s", True)

    if has_logic_operator is None:
        constraints = [expr]

    logger.debug(">>> Complex symbooglix constraints: %s", constraints)

    return has_negation_operator, has_logic_operator, constraints


def to_constraint(symbooglix_constraint):

    # split constraints into its three distinct parts.
    left, op, right = split_constraint(symbooglix_constraint)

    # remove any symbolic prefixes and suffixes.
    left  = remove_symbolic_prefix_and_suffix(left)
    op    = remove_symbolic_prefix_and_suffix(op)
    right = remove_symbolic_prefix_and_suffix(right)

    # rearrange assignment if value is on the left-hand side.
    if left.isdigit() and not right.isdigit():
        left, op, right = rearrange_assignment(left, op, right)

    # check for negation in constraint.
    if left.startswith('!'):
        left = left[1:]
        op = negate_operator(op)

    # parse boolean constraints.
    # if is_boolean_heap_access(left, op, right):
    #     left, op, right = parse_boolean_heap_access(left, op, right)

    # parse integer constraints.
    if is_integer_heap_access(left, op, right):
        left, op, right = parse_integer_heap_access(left, op, right)

    # parse object constraints.
    # if is_object_heap_access(left, op, right):
    #     left, op, right = parse_object_heap_access(left, op, right)

    return Constraint(left, op, right)


def split_constraint(string):

    # list supported operators.
    delimiters = "(==)", "(!=)", "(>=)", "(<=)", "(>)", "(<)"
    pattern = '|'.join(delimiters)

    # split given string.
    c = re.split(pattern, string)
    c = filter(lambda x: x is not None, c)

    # retrieve information and add missing information for boolean constraints.
    left  = c[0].strip()
    op    = c[1].strip() if len(c) > 1 else '=='
    right = c[2].strip() if len(c) > 2 else 'true'

    return left, op, right


def remove_symbolic_prefix_and_suffix(string):

    # remove prefix, i.e., '~sb_'.
    string = re.sub(r'[/~]sb_', '', string)

    # remove suffix, e.g., '_0' or '_99'.
    string = re.sub(r'_[\d]*', '', string)

    return string


def rearrange_assignment(left, op, right):

    # check for certain operators.
    if op == ">" or op == ">=" or op == "<" or op == "<=":
        op = negate_operator(op)

    return right, op, left


def negate_operator(op):
    if op == '==':
        op = '!='
    elif op == '!=':
        op = '=='
    elif op == '<':
        op = '>='
    elif op == '<=':
        op = '>'
    elif op == '>':
        op = '<='
    elif op == '>=':
        op = '<'
    else:

        logger.error("The following operator not supported: %s", op)

        raise Exception('cannot create negation of op')

    return op


def is_boolean_heap_access(left, op, right):

    if left.startswith("boolHeap") or left.startswith("!boolHeap"):
        return True

    return False


def parse_boolean_heap_access(left, op, right):

    # split heap access into pieces.
    heap, fields = unpack_heap_access(left)

    # remove heap history by focusing on the last field.
    if len(fields) > 2:

        # filter heap assignments.
        fields = filter(lambda field: not is_boolean_heap_assignment(field), fields)

        # build new heap.
        left = heap + reduce(lambda x, y: x + "[" + y + "]", fields, "")

    return left, op, right


def is_boolean_heap_assignment(string):
    left, op, right = parse_to_assignment(string)

    if not left == '' and not right == '':
        return True

    return False


def is_integer_heap_access(left, op, right):

    if left.startswith("intHeap"):
        return True

    if not left.isdigit() and right.isdigit():
        return True

    return False


def parse_integer_heap_access(left, op, right):

    # check for adding prefix in variable declaration.
    if " + intHeap" in left:
        value, variable = left.split(" + ", 1)

        # check if left-hand side of variable declaration is numerical.
        if value.isdigit() or value[1:].isdigit():

            # perform arithmetic operations.
            left = variable
            right = str(int(right) - int(value))

    # check for substituting prefix in variable declaration.
    elif " - intHeap" in left:
        value, variable = left.split(" - ", 1)

        # check if left-hand side of variable declaration is numerical.
        if value.isdigit() or value[1:].isdigit():

            # perform arithmetic operations.
            left = variable
            right = str((int(right) - int(value)) * (-1))

    return left, op, right


def is_object_heap_access(left, op, right):

    if left.startswith("objHeap"):
        return True

    return False


def parse_object_heap_access(left, op, right):

    # split heap access into pieces.
    heap, fields = unpack_heap_access(left)

    # remove heap history by focusing on the last field.
    if len(fields) > 2:

        # filter heap assignments.
        fields = filter(lambda field: not is_inner_heap_assignment(field), fields)

        # build new heap.
        left = heap + reduce(lambda x, y: x + "[" + y + "]", fields, "")

    return left, op, right


def is_inner_heap_assignment(string):
    left, op, right = parse_to_assignment(string)

    if not left == '' and not right == '':
        return True

    return False


def unpack_heap_access(string):

    # retrieve heap information.
    heap = string.split("[",1)[0]

    # check if string encapsulates heap definition.
    if not heap:
        return "", []

    # split heap definition from string.
    string = string.split(heap,1)[-1]

    # specify list of all fields.
    fields = []

    # iterate all fields.
    while not string == '':

        # parse field within first parenthesis.
        field = parse_string_in_parenthesis(string)

        # split parsed field definition.
        string = string.split(field,1)[-1]

        # remove tailing ']'.
        if string.startswith(']'):
            string = string[1:]

        # append to list of fields.
        fields.append(field)

    return heap, fields


def parse_string_in_parenthesis(string):
    stack = []

    s = []
    for c in string:
        if c == "[" and len(stack) is 0:
            stack.append(c)

        elif c == "[" and len(stack) > 0:
            s.append(c)

            stack.append(c)
        elif c == "]" and len(stack) is 0:
            return ""

        elif c == "]" and len(stack) is 1:
            break;

        elif c == "]":
            s.append(c)
            stack.pop()

        elif stack:
            s.append(c)

    return ''.join(s)


def to_effects(symbooglix_state):
    effects = []

    # check if booHeap information is empty.
    if symbooglix_state.memory['globals'].has_key('boolHeap') \
            and not symbooglix_state.memory['globals']['boolHeap']['expr'] == "~sb_boolHeap_0":

        # retrieve booHap information.
        effect = symbooglix_state.memory['globals']['boolHeap']['expr']

        # clean information by removing symbolic prefix and symbolic suffix.
        effect = remove_symbolic_prefix_and_suffix(effect)

        # parse effects.
        # effect = parse_heap(effect)

        # append to effect memory.
        effects.append(effect)

    # check if intHeap information is empty.
    if symbooglix_state.memory['globals'].has_key('intHeap') \
            and not symbooglix_state.memory['globals']['intHeap']['expr'] == "~sb_intHeap_0":

        # retrieve intHeap information.
        effect = symbooglix_state.memory['globals']['intHeap']['expr']

        # clean information by removing symbolic prefix and symbolic suffix.
        effect = remove_symbolic_prefix_and_suffix(effect)

        # parse effects.
        # effect = parse_heap(effect)

        # append to effect summary.
        effects.append(effect)

    # check if objHeap information is empty.
    if symbooglix_state.memory['globals'].has_key('objHeap') \
            and not symbooglix_state.memory['globals']['objHeap']['expr'] == "~sb_objHeap_0":

        # retrieve obHeap information.
        effect = symbooglix_state.memory['globals']['objHeap']['expr']

        # clean information by removing symbolic prefix and symbolic suffix.
        effect = remove_symbolic_prefix_and_suffix(effect)

        # parse effects.
        # effect = parse_heap(effect)

        # append to effect summary.
        effects.append(effect)

    return effects


def parse_heap(string):
    try:
        effect = unpack_heap(string)
    except Exception:

        effect = string

    return effect


def unpack_heap(string):

    logger.info("Analysing heap information: %s", string)

    # e.g. heap[obj := heap[obj][field][field]]
    if check_if_nested_heap_access(string):

        # retrieve the nested information.
        # TODO: Refactor!
        # TODO: Add check that left-hand side is not a heap access itself.
        _, obj, _   = parse_to_heap_access(string)
        _, _, right = parse_to_assignment(obj)

        logger.debug("Unpacked nested heap information: %s", right)

        return unpack_heap(right)

    # e.g. heap[obj][field][field]
    if check_if_heap_access(string):

        # retrieve heap information.
        heap, obj, fields = parse_to_heap_access(string)

        logger.debug("Unpacked heap type information: %s", heap)
        logger.debug("Unpacked object information: %s", obj)
        logger.debug("Unpacked fields information: %s", str(fields))

        # continue unpacking obj.
        obj = unpack_heap(obj)

        # continue unpacking fields.
        fs = []
        for f in fields:
            field = unpack_heap(f)
            fs.append(field)

        # combine unpacked information.
        return heap + "[" + obj + "]" + reduce(lambda x,y: x + "[" + y + "]",fields,"")

    return string


def parse_to_heap_access(string):

    # retrieve heap information.
    heap = string.split("[",1)[0]

    # retrieve object information.
    obj = parse_string_in_first_parenthesis(string)

    # cut object information.
    string = ''.join(string.split(heap + "[" + obj + "]",1)[1:])

    # array of fields.
    fields = []

    # cut field information.
    field = parse_string_in_first_parenthesis(string)

    while field is not '':
        # append field information
        fields.append(field)

        # cut next field information
        string = ''.join(string.split("[" + field + "]",1)[1:])

        # parse field information
        field = parse_string_in_first_parenthesis(string)

    # return heap access
    return heap, obj, fields


def parse_to_assignment(string):
    stack = []

    left = []

    # find left-hand side of assignment
    for c in string:

        # no opening bracket and beginning of assignment.
        if not stack and c == ':':
            break;

        # push opening bracket to memory.
        if c == "[":
            stack.append(c)

        # pop opening bracket from memory.
        if c == "]":
            stack.pop()

        # append char to variable.
        left.append(c)

    # cast char array to string.
    left = ''.join(left)

    right = ""

    # find right-hand side of assignment
    if left is not '':
        right = string.split(left,1)[1]
        right = right[3:]
        left = left[:-1]

    return left, "", right


def parse_string_in_first_parenthesis(string):
    stack = []

    s = []
    for c in string:
        if c == "[" and len(stack) is 0:
            stack.append(c)
        elif c == "[" and len(stack) > 0:
            s.append(c)
            stack.append(c)
        elif c == "]" and len(stack) is 0:
            return ""
        elif c == "]" and len(stack) is 1:
            break;
        elif c == "]":
            s.append(c)
            stack.pop()
        elif stack:
            s.append(c)

    return ''.join(s)


def check_if_heap_access(string):
    heap, obj, field = parse_to_heap_access(string)

    if heap.startswith("boolHeap") \
            or heap.startswith("intHeap") \
            or heap.startswith("objHeap"):

        return True if not obj == '' and not field == [] else False

    return False


def check_if_nested_heap_access(string):
    heap, obj, fields = parse_to_heap_access(string)

    if heap.startswith("boolHeap") \
            or heap.startswith("intHeap") \
            or heap.startswith("objHeap"):

        if not fields == []:
            return False

        left, _, right = parse_to_assignment(obj)

        if right.startswith("boolHeap") \
                or right.startswith("intHeap") \
                or right.startswith("objHeap"):

            return True

    return False


def check_if_assignment(string):
    left, _, right = parse_to_assignment(string)

    return True if left and right else False


def to_trace(symbooglix_state):
    symbooglix_memory = symbooglix_state.memory

    # some string modifications.
    trace = symbooglix_memory['globals']['callStack']['expr']
    trace = trace.split('sb_callStack_0')[1]
    trace = trace[1:].split("[")
    trace = map(lambda x: x[0:-3].split('~sb_',2)[2],trace)
    return trace