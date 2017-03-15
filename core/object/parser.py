import re

from core.object.data.solver     import Program, SymbolicState, Condition, Constraint
from core.object.data.symbooglix import SymbooglixConstraintIterator
from core.utils                  import logger

def to_program(terminated_symbooglix_states):
    program = Program()

    # iterate terminated states of symbolically executed program
    for symbooglix_state in terminated_symbooglix_states:

        logger.info("Extracting state's id.%s", '')

        # retrieve id.
        id = to_id(symbooglix_state)

        logger.info("Extracting state's conditions.%s", '')

        # retrieve conditions.
        conditions = to_conditions(symbooglix_state)

        logger.info("Extracting state's trace.%s", '')

        # retrieve trace.
        trace = to_trace(symbooglix_state)

        logger.info("Combining state's information.%s", '')

        # create symbolic state
        state = SymbolicState(id, conditions, trace)

        logger.info("Adding state's information to program.%s", '')

        # add identified state.
        program.states.append(state)

    return program

def to_id(symbooglix_state):
    return symbooglix_state.state_id

def to_conditions(symbooglix_state):
    # list of conditions.
    conditions = []

    # iterate constraints of terminated state
    for symbooglix_constraint in SymbooglixConstraintIterator(symbooglix_state):
        # retrieve information in "expr".
        constraint = symbooglix_constraint['expr']


        if constraint == 'true':
            # constraint = symbooglix_constraint['origin']
            # constraint = constraint.split('[Cmd] assume {:partition}')[1]
            # constraint = constraint.strip()
            # constraint = constraint.replace(';','')
            continue

        logger.debug("> Analysing symbooglix constraint: %s", constraint)

        # split symbooglix constraints into its nested parts
        has_negation_operator, symbooglix_nested_constraints = split_complex_constraint(constraint)

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

        #
        com = '' if len(nested_constraints) == 1 else '&&'

        # generate condition.
        condition = Condition(has_negation_operator, com, nested_constraints)

        logger.debug("> Generated condition: %s", condition)

        # add to collected conditions.
        conditions.append(condition)

    return conditions


def split_complex_constraint(expr):
    delimiters = '&&'

    has_negation_operator = True if delimiters in expr and expr.startswith('!(') else False

    if has_negation_operator:
        expr = expr[2:-1]

    pattern = '|'.join(map(re.escape, delimiters))
    constraints = re.split(pattern, expr)

    return has_negation_operator, constraints


def split(string, *delimiters):
    pattern = '|'.join(map(re.escape, delimiters))
    return re.split(pattern, string)


def to_constraint(symbooglix_constraint):
    c = symbooglix_constraint.split()

    var = c[0]
    op  = c[1] if len(c) > 1 else '=='
    val = c[2] if len(c) > 2 else 'true'

    # TODO: Find better solution to handle symbooglix prefixes.
    var = var.replace('~sb_','')
    var = var.replace('_0', '')
    val = val.replace('~sb_','')
    val = val.replace('_0', '')

    logger.info("Parsing to z3 constraint.%s", '')
    logger.debug(">> var: %s", var)
    logger.debug(">> op:  %s", op)
    logger.debug(">> val: %s", val)


    if var.startswith('!'):
        constraint = Constraint(var[1:], neg(op), val)
    else:
        constraint = Constraint(var, op, val)

    return constraint


def neg(op):
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
        print op
        raise Exception('cannot create negation of op')

    return op


def to_trace(symbooglix_state):
    symbooglix_memory = symbooglix_state.memory

    # some string modifications.
    trace = symbooglix_memory['globals']['callStack']['expr']
    trace = trace.split('sb_callStack_0')[1]
    trace = trace[1:].split("[")
    trace = map(lambda x: x[0:-3].split('~sb_',2)[2],trace)
    return trace