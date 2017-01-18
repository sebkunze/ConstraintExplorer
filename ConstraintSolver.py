#!/usr/bin/env python
import os, sys

from optparse       import OptionParser # Depricated in 2.7; Use argparse instead!

from core           import analyser
from core.interface import console
from core.io        import loader, dumper
from core.utils     import logger

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

    logger.info('Analysing source files: %s', source_files)

    # interpreting specified program variants.
    programs = loader.load_programs(source_files)

    # for source_file in source_files:
    #     name = os.path.basename(os.path.normpath(source_file))
    #     logger.info('Source file: %s', name)

    print 'Comparing program states:\n   ' + source_files[0] + '\n   ' + source_files[1]

    # analysing programs' states.
    equivalent_states, overlapping_states, new_states = \
        analyser.analyse_program_states(programs[0], programs[1])

    # overlapping_values = analyser.generate_values_for_overlapping_states(overlapping_states)

    # new_values         = analyser.generate_values_for_new_states(new_states)

    # fetching output directory.
    output_file = options.output

    logger.info('Writing analysed program states to: %s', output_file)

    # exporting analysed programs' states.
    dumper.dump(equivalent_states, overlapping_states, new_states, output_file)

if __name__ == '__main__':
    main()