import re

from z3 import Bool, Int, And, Not

from core.object.data.solver     import Program, SymbolicState, Constraint
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

            # split complex constraints into individual parts
            has_negation_operator, symbooglix_sub_constraints = split_complex_constraint(origin)

            # nested z3 constraints.
            sub_z3_constraints = []

            # iterate individual parts of complex constraint.
            for symbooglix_sub_constraint in symbooglix_sub_constraints:
                # TODO: Splitting constraints seems to have some side-effect!
                if symbooglix_sub_constraint == '':
                    continue

                # strip whitespaces on the both side.
                symbooglix_sub_constraint = symbooglix_sub_constraint.strip()

                # remove parentheses on both sides.
                if symbooglix_sub_constraint.startswith('('):
                    symbooglix_sub_constraint = symbooglix_constraint[1:-1]

                logger.debug("Parsing symbooglix sub-constraint: %s", symbooglix_sub_constraint)

                sub_z3_constraint = None

                # parse to z3 constraint.
                if   is_boolean_constraint(symbooglix_sub_constraint):
                    sub_z3_constraint = to_boolean_constraint(symbooglix_sub_constraint)
                elif is_integer_constraint(symbooglix_sub_constraint):
                    sub_z3_constraint = to_integer_constraint(symbooglix_sub_constraint)

                # TODO: Figure out where newline commands come from!
                logger.debug("Parsed to z3 constraint: %s", str(sub_z3_constraint).replace('\n',''))

                sub_z3_constraints.append(sub_z3_constraint)

            # collapse nested z3 constraints.
            z3_constraint = reduce(lambda x,y: And(x,y), sub_z3_constraints)

            # handle negation operator for complex constraints.
            if has_negation_operator:
                z3_constraint = Not(z3_constraint )

            logger.debug("Collapsed to z3 constraint: %s", str(z3_constraint).replace('\n',''))

            # add to state constraints.
            state_constraints.append(Constraint(z3_constraint))

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

def is_boolean_constraint(constraint):
    # handle parenthesis.
    constraint.replace('(','')
    constraint.replace(')','')

    # handle negating operator.
    if constraint.startswith('!'):
        constraint = constraint[1:]

    is_boolean_constraint = constraint[0] is 'b'

    return is_boolean_constraint

def to_boolean_constraint(constraint):
    c = constraint.split()

    z3 = None

    if len(c) < 2:
        # split constraint in variable.
        var = c[0]

        logger.debug("Found boolean variable: %s", var)

        if var.startswith('!'):
            z3 = Not(Bool(var[1:]))
        else:
            z3 = Bool(var)
    else:
        # split constraint in variable, operator, and value.
        var = c[0]
        op  = c[1]
        val = c[2]

        # TODO: Check what is wrong with the logger when using multiple parameters.
        # debug("Split constraint in variable: %s, operator: %s, and value: %s", [var, op, val])
        logger.debug("Found variable: %s", var)
        logger.debug("Found operator: %s", op)
        logger.debug("Found value: %s", val)

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

    return z3

def is_integer_constraint(constraint):
    # handle parenthesis.
    constraint.replace('(','')
    constraint.replace(')','')

    # handle negating operator.
    if constraint.startswith('!'):
        constraint = constraint[1:]

    is_integer_constraint = constraint[0] is 'i'

    return is_integer_constraint

def to_integer_constraint(constraint):
    c = constraint.split()

    # split constraint in variable, operator, and value.
    var = c[0]
    op  = c[1]
    val = c[2]

    z3 = None

    # TODO: Check what is wrong with the logger when using multiple parameters.
    # debug("Split constraint in variable: %s, operator: %s, and value: %s", [var, op, val])
    logger.debug("Found integer variable: %s", var)
    logger.debug("Found operator: %s", op)
    logger.debug("Found value: %s", val)

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

    return z3