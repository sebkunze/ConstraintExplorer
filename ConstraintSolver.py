import os
import sys

from optparse       import OptionParser # Depricated in 2.7; Use argparse instead!
from core           import analyser
from core           import symbooglix
from core.interface import console
from core.io        import dumper
from core.data      import program

PROG = os.path.basename(os.path.splitext(__file__)[0])

VERSION = '0.1'

def main():
    # Creating console interface.
    parser = OptionParser(option_class = console.MultipleOption,
                          usage        = 'usage: %prog [options] arg1 arg2',
                          version      = '%s %s' % (PROG, VERSION))
    console.populate_option_parser(parser)

    # Retrieving given options.
    options, args = parser.parse_args()

    # Asserting input options.
    if len(sys.argv) == 1 or options.inputs is None:
        parser.parse_args(['--help'])

    # Fetching program variants.
    paths = options.inputs

    # Interpreting specified program variants.
    programs = []
    for path in paths:
        terminated_symbooglix_states = symbooglix.read_terminated_symbooglix_states(path)
        translated_program = program.translate_to_program(terminated_symbooglix_states)
        programs.append(translated_program)

    # Analysing programs' states.
    equivalent_states, overlapping_states, new_states = \
        analyser.analyse_program_states(programs[0], programs[1])

    # Exporting analysed programs' states.
    dumper.dump(equivalent_states, overlapping_states, new_states)

if __name__ == '__main__':
    main()