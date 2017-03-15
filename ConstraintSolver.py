#!/usr/bin/env python
from argparse       import ArgumentParser

from core           import analyser
from core.io        import loader, dumper

VERSION = '0.1'

def main():
    # creating console interface
    parser = ArgumentParser(description="analysing terminated states of two products.")

    # adding positional arguments.
    parser.add_argument("sources", help="input source files.", nargs="+")

    # adding optional arguments
    parser.add_argument("-t", "--target", help="output target file.", default="out.yml")

    # adding mutually exclusive arguments.
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-v", "--verbose", action="store_true")
    group1.add_argument("-q", "--quit",    action="store_true", default=1)

    # adding mutually exclusive arguments.
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-a", "--analyse-states", action="store_true")
    group2.add_argument("-c", "--compare-states", action="store_true", default=1)

    # populating parser.
    options = parser.parse_args()

    # fetching program variants.
    source_files = options.sources

    # fetching output directory.
    output_file = options.target

    # interpreting specified program variants.
    programs = loader.load_programs(source_files)

    if options.analyse_states:
        # analysing programs' states.
        tests = analyser.analyse_program_states(programs[0])

        # exporting analysed programs' states.
        dumper.dump(tests, output_file)

    elif options.compare_states:
        # comparing programs' states.
        tests = analyser.compare_program_states(programs[0], programs[1])

        # exporting analysed programs' states.
        dumper.dump(tests, output_file)

if __name__ == '__main__':
    main()