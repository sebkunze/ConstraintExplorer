import re

from z3              import Bool, Int, And, Not

from core.object.data.symbooglix import SymbooglixConstraintIterator
from core.utils.logger import debug


class Program:
    def __init__(self, terminated_states = []):
        self.terminated_states = terminated_states

    def __repr__(self):
        return "%s(terminated_states: %s)" % (
            self.__class__.__name__, self.terminated_states)

    def add_terminated_state(self, terminated_state):
        self.terminated_states.append(terminated_state)


class TerminatedSymbolicState:
    def __init__(self, id = None, constraints = []):
        self.id          = id
        self.constraints = constraints

    def __repr__(self):
        return "%s(id: %s, constraints: %s)" % (
            self.__class__.__name__, self.id, self.constraints)

class Constraint:
    def __init__(self, z3constraint):
        self.z3constraint = z3constraint

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__, self.z3constraint)
        return str(self.z3constraint)

def translate_to_program(terminated_symbooglix_states):
    program = Program([])

    # iterate terminated states of symbolically executed program
    for symbooglix_state in terminated_symbooglix_states:

        state_id          = symbooglix_state.state_id
        state_constraints = []

        debug("Parsing state: %s", state_id)

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

            # log origin for debugging.
            debug("Analysing symbooglix constraint: %s", origin)

            # nested z3 constraints.
            constraints = []

            # split complex constraints into individual parts
            has_negation_operator, symbooglix_constraints = split_complex_constraint(origin)

            debug("%s", has_negation_operator)
            debug("%s", symbooglix_constraints)

            # iterate individual parts of complex constraint.
            for symbooglix_constraint in symbooglix_constraints:
                # TODO: Splitting constraints seems to have some side-effect!
                if symbooglix_constraint == '':
                    continue

                # strip whitespaces on the both side.
                symbooglix_constraint = symbooglix_constraint.strip()

                # remove parentheses on both sides.
                if symbooglix_constraint.startswith('('):
                    symbooglix_constraint = symbooglix_constraint[1:-1]

                # log symbooglix constraint for debugging.
                debug("Parsing symbooglix constraint: %s", symbooglix_constraint)

                sub_constraint = None

                # parse to z3 constraint.
                if is_boolean_constraint(symbooglix_constraint):
                    sub_constraint = to_boolean_constraint(symbooglix_constraint)
                elif is_integer_constraint(symbooglix_constraint):
                    sub_constraint = to_integer_constraint(symbooglix_constraint)

                # log z3 constraint for debugging.
                debug("Parsed to z3 constraint: %s", sub_constraint)

                constraints.append(sub_constraint)

            # collapse nested z3 constraints.
            constraint = reduce(lambda x,y: And(x,y), constraints)

            # handle negation operator for complex constraints.
            if has_negation_operator:
                constraint = Not(constraint)

            # log collapsed constraint for debugging.
            debug("Collapsed to z3 constraint: %s", constraint)

            # add to state constraints.
            state_constraints.append(constraint)

        # create terminated state.
        state = TerminatedSymbolicState(state_id, state_constraints)

        # add terminated state to program.
        program.add_terminated_state(state)

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

    if len(c) < 2:
        # split constraint in variable.
        var = c[0]

        debug("Found variable: %s", var)

        if var.startswith('!'):
            return Not(Bool(var[1:]))
        else:
            return Bool(var)
    else:
        # split constraint in variable, operator, and value.
        var = c[0]
        op  = c[1]
        val = c[2]

        # TODO: Check what is wrong with the logger when using multiple parameters.
        # debug("Split constraint in variable: %s, operator: %s, and value: %s", [var, op, val])
        debug("Found variable: %s", var)
        debug("Found operator: %s", op)
        debug("Found value: %s", val)

        if not var.startswith('!'):
            if op == '==' or op == '<==>':
                if val == 'true' or val == '!false':
                    return Bool(var) == True
                else:
                    return Bool(var) == False
            else:
                if val == 'true' or val == '!false':
                    return Bool(var) != True
                else:
                    return Bool(var) != False
        else:
            var = var[1:]
            if op == '==' or op == '<==>':
                if val == 'true' or val == '!false':
                    return Bool(var) != True
                else:
                    return Bool(var) != False
            else:
                if val == 'true' or val == '!false':
                    return Bool(var) == True
                else:
                    return Bool(var) == False

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

    # TODO: Check what is wrong with the logger when using multiple parameters.
    # debug("Split constraint in variable: %s, operator: %s, and value: %s", [var, op, val])
    debug("Found variable: %s", var)
    debug("Found operator: %s", op)
    debug("Found value: %s", val)

    if not var.startswith('!'):
        if op == '==' or op == '<==>':
            if val.isdigit():
                return Int(var) == val
            else:
                return Int(var) == Int(val)
        else:
            if val.isdigit():
                return Int(var) != val
            else:
                return Int(var) != Int(val)
    else:
        if op == '==' or op == '<==>':
            if val.isdigit():
                return Int(var) != val
            else:
                return Int(var) != Int(val)
        else:
            if val.isdigit():
                return Int(var) == val
            else:
                return Int(var) == Int(val)