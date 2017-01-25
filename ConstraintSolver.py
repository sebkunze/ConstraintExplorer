#!/usr/bin/env python
import os, sys

from optparse       import OptionParser # Depricated in 2.7; Use argparse instead!

from core           import analyser
from core.interface import console
from core.io        import loader, dumper

PROG = os.path.basename(os.path.splitext(__file__)[0])

VERSION = '0.1'

def main():
    # creating console interface.
    parser = OptionParser(option_class = console.MultipleOption,
                          usage        = 'usage: %prog [options] arg1 arg2',
                          version      = '%s %s' % (PROG, VERSION))

    console.populate_option_parser(parser)

    # retrieving given options.
    options, args = parser.parse_args()

    # asserting input options.
    if len(sys.argv) == 1 or options.inputs is None:
        parser.parse_args(['--help'])

    # fetching program variants.
    source_files = options.inputs

    # interpreting specified program variants.
    programs = loader.load_programs(source_files)

    # analysing programs' states.
    tests = analyser.analyse_program_states(programs[0], programs[1])

    # fetching output directory.
    output_file = options.output

    # exporting analysed programs' states.
    dumper.dump(tests, output_file)

if __name__ == '__main__':
    main()