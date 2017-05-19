#!/usr/bin/env python
import os

from argparse       import ArgumentParser

from core           import analyser
from core.io        import loader, dumper
from core.utils     import report

VERSION = '0.1'

def main():
    # creating console interface
    parser = ArgumentParser(description="analysing terminated states of two products.")

    # adding positional arguments.
    parser.add_argument("sources", help="input source files.", nargs="+")

    # adding optional arguments
    parser.add_argument("-r", "--report", help="output report file.", default="out.json")

    # adding optional arguments
    parser.add_argument("-t", "--target", help="output directory.", default="out.yml")

    # adding mutually exclusive arguments.
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-v", "--verbose", action="store_true")
    group1.add_argument("-q", "--quiet",    action="store_true", default=1)

    # adding mutually exclusive arguments.
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-a", "--analyse-states", action="store_true")
    group2.add_argument("-c", "--compare-states", action="store_true", default=1)

    # populating parser.
    options = parser.parse_args()

    # fetching program variants.
    source_files = options.sources

    # fetching output directory.
    output_directory = options.target

    # interpreting specified program variants.
    programs = loader.load_programs(source_files)

    if options.analyse_states:
        # analysing programs' states
        create = analyser.analyse_program_states(programs[0])

        # save number of created states to report.
        report.states[report.CREATE] = len(create)

        # exporting analysed programs' states.
        dumper.dump_analysis_output(output_directory, create)

    elif options.compare_states:
        # comparing programs' states.
        create, skip, adjust = analyser.compare_program_states(programs[0], programs[1])

        # save number of created states to report.
        report.states[report.CREATE] = len(create)

        # save number of skipped states to report.
        report.states[report.SKIP] = len(skip)

        # save number of adjusted states to report.
        report.states[report.ADJUST] = len(adjust)

        # exporting analysed programs' states.
        dumper.dump_comparison_output(output_directory, create, skip, adjust)

    # write report to specified file.
    report.dump(options.report)

if __name__ == '__main__':
    main()