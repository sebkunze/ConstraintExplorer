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

        logger.info("Parsing state: %s", state_id)

        # iterate constraints of terminated state
        for symbooglix_constraint in SymbooglixConstraintIterator(symbooglix_state):
            # retrieve information in "origin"
            origin = symbooglix_constraint['origin']

            # remove suffix ";"
            needle = ';'
            if needle in origin:
                origin, _ = origin.split(needle, 1)

            # remove prefix "[Cmd] assume {:partition}"
            needle = '[Cmd] assume {:partition} '
            if needle in origin:
                _, origin = origin.split(needle, 1)

            logger.debug("Analysing symbooglix constraint: %s", origin)

            # split symbooglix constraints into its nested parts
            has_negation_operator, symbooglix_nested_constraints = split_complex_constraint(origin)

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
            if   len(nested_constraints) > 1:
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

        # create terminated state.
        state = SymbolicState(state_id, state_constraints)

        # add terminated state to program.
        program.add_symbolic_state(state)

    return program

def split_complex_constraint(constraint):
    delimiters = '&&'

    has_negation_operator = True if delimiters in constraint and constraint.startswith('!(') else False

    if has_negation_operator:
        constraint = constraint[2:-1]

    pattern = '|'.join(map(re.escape, delimiters))
    constraints = re.split(pattern, constraint)

    return has_negation_operator, constraints

def split(string, *delimiters):
    pattern = '|'.join(map(re.escape, delimiters))
    return re.split(pattern, string)

def to_constraint(symbooglic_constraint):
    c = symbooglic_constraint.split()

    if len(c) < 2:
        var = c[0]

        if var.startswith('!'):
            return SimpleConstraint(True, var[1:], '==', 'true')
        else:
            return SimpleConstraint(False, var   , '==', 'true')
    else:
        var = c[0]
        op  = c[1]
        val = c[2]

        if var.startswith('!'):
            return SimpleConstraint(True, var[1:], op, val)
        else:
            return SimpleConstraint(False, var, op, val)