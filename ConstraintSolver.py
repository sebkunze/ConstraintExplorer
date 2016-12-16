# TODO: Move this somehow without destroying dependencies!
class TerminatedSymbooglixState:
    def __init__(self, state_id, memory, constraints):
        self.state_id    = state_id
        self.memory      = memory       # TODO: Figure out of memory is required!
        self.constraints = constraints

    # TODO: Figure out if the following code is necessary!
    def get_state_id(self):
        return self.state_id

    def get_memory(self):
        return self.memory

    def get_constraints(self):
        return self.constraints


import os, sys
from core         import symbooglix
from core         import interpreter
from core         import analyser
from optparse import OptionParser
from optparse import Option, OptionValueError

VERSION = '0.1'

class MultipleOption(Option):

    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            lvalue = value.split(",")
            values.ensure_value(dest, []).extend(lvalue)
        else:
            Option.take_action(
                self, action, dest, opt, value, values, parser)

def main():
    PROG = os.path.basename(os.path.splitext(__file__)[0])
    parser = OptionParser(option_class=MultipleOption,
                          usage='usage: %prog [OPTIONS] COMMAND [BLOG_FILE]',
                          version='%s %s' % (PROG, VERSION))

    parser.add_option("-i", "--input-files",
                  action="extend", type="string",
                  dest="inputs",
                  metavar="FILE",
                  help="specified input FILE(S)")
    parser.add_option("-o", "--output_file", action="extend", dest="output",
                  help="defined output to FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=False,
                  help="do print status messages to stdout")
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose",
                  help="don't print status messages to stdout")


    options, args = parser.parse_args() # TODO: print version

    if len(sys.argv) == 1:
        parser.parse_args(['--help'])

    # Fetching program variants.
    paths = options.inputs

    # Interpreting specified program variants.
    programs = []
    for path in paths:
        states = symbooglix.read_terminated_symbooglix_states(path)
        program = interpreter.translate_to_program(states)
        programs.append(program)

    # Feeding interpreted program variants to z3
    statesX = programs[0].terminated_states
    statesY = programs[1].terminated_states

    equivalentStates = []
    newStates = range(len(statesY))
    overlappingStates = []

    print "Assuming number of covered states: " + str(len(statesX))
    print "Number of states to be covered: " + str(len(statesY))

    for stateY in statesY:
        equivalentToStatesInX = analyser.generate_list_of_equivalent_states(stateY, statesX)
        # equivalentStates.append(filter(lambda x: x is not None, map(lambda x: (stateY.id, equivalentToStatesInX.index(x)) if x is True else None, equivalentToStatesInX)))
        pos = [equivalentToStatesInX.index(y) for y in equivalentToStatesInX if y is True]
        if pos:
            equivalentStates.append((stateY.id, pos[0]))

    print "equivalent states; test cases to be skipped:\t" + str(equivalentStates)

    for stateY in statesY:
        overlappingWithStateInX = analyser.generate_list_of_overlapping_states(stateY, statesX)
        pos = [overlappingWithStateInX.index(y) for y in overlappingWithStateInX if y]
        if pos:
            overlappingStates.append((stateY.id, pos[0]))
            newStates.remove(stateY.id)

    overlappingStates = filter(lambda x: x not in equivalentStates, overlappingStates)

    print "overlapping states; test cases to be refined:\t" + str(overlappingStates)
    print "new states; test cases to be created:\t\t" + str(newStates)

if __name__ == '__main__':
    main()