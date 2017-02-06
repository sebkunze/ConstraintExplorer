import re

from core.object.data.solver     import Program, SymbolicState, SimpleConstraint, ComplexConstraint
from core.object.data.symbooglix import TerminatedSymbooglixState, SymbooglixConstraintIterator
from core.utils                  import logger


def to_program(terminated_symbooglix_states):
    program = Program([])

    # iterate terminated states of symbolically executed program
    for symbooglix_state in terminated_symbooglix_states:

        state_id          = symbooglix_state.state_id
        state_constraints = []
        state_memory      = symbooglix_state.memory

        logger.info("Parsing state: %s", state_id)

        # iterate constraints of terminated state
        for symbooglix_constraint in SymbooglixConstraintIterator(symbooglix_state):
            # retrieve information in "expr".
            expr = symbooglix_constraint['expr']

            logger.debug("Analysing symbooglix constraint: %s", expr)

            # skip symbooglix constraints that are part of other symbooglix constraints, thus evaluating to true.
            if expr == 'true':
                continue

            # split symbooglix constraints into its nested parts
            has_negation_operator, symbooglix_nested_constraints = split_complex_constraint(expr)

            # list of nested constraints.
            nested_constraints = []

            # iterate individual parts of complex constraint.
            for symbooglix_nested_constraint in symbooglix_nested_constraints:
                # TODO: Splitting nested constraints seems to have side-effect in some cases; needs some further investigation!
                if symbooglix_nested_constraint == '':
                    continue

                # strip whitespaces on the both side.
                symbooglix_nested_constraint = symbooglix_nested_constraint.strip()

                # remove parentheses on both sides.
                if symbooglix_nested_constraint.startswith('('):
                    symbooglix_nested_constraint = symbooglix_constraint[1:-1]

                logger.debug("Parsing symbooglix nested constraint: %s", symbooglix_nested_constraint)

                # parse to nested constraint.
                nested_constraint = to_constraint(symbooglix_nested_constraint)

                logger.debug("Parsed to nested constraint: %s", nested_constraint)

                # add to nested constraint.
                nested_constraints.append(nested_constraint)

            # collapse nested constraints.
            if len(nested_constraints) > 1:
                # TODO: To this end, we support the &&-operator only.
                logger.debug("Collapse nested constraints%s", '.')
                constraint = ComplexConstraint(has_negation_operator, '&&', nested_constraints)
            else:
                logger.debug("Collapse non-nested constraints%s", '.')
                constraint = nested_constraints[0]
                if has_negation_operator:
                    logger.debug("- Toggle constraint%s", '.')
                    constraint.toggle()

            logger.debug("Generated to constraint: %s", constraint)

            # add constraint to symbolic state.
            state_constraints.append(constraint)

        #
        state_trace = to_stack_trace(state_memory)

        # create terminated state.
        state = SymbolicState(state_id, state_constraints, state_trace)

        # add terminated state to program.
        program.add_symbolic_state(state)

    return program


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

    # TODO: Find better solution!
    var = var.replace('~sb_','')
    var = var.replace('_0', '')
    val = val.replace('~sb_','')
    val = val.replace('_0', '')

    if var.startswith('!'):
        constraint = SimpleConstraint(True, var[1:], op, val )
    else:
        constraint = SimpleConstraint(False, var, op, val)

    return constraint

def to_stack_trace(symbooglix_memory):
    # some string modifications.
    trace = symbooglix_memory['globals']['callStack']['expr']
    trace = trace.split('sb_callStack_0')[1]
    trace = trace[1:].split("[")
    trace = map(lambda x: x[0:-3].split('~sb_',2)[2],trace)
    return trace