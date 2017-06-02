import os
import yaml

from core.utils import logger


conf_enable_references = False


def dump_analysis_output(output_directory, create):

    # create directory if non existing.
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    # specify path for created states.
    path = os.path.join(output_directory, "create.yml")

    # save created states.
    dump(path, create)


def dump_comparison_output(output_directory, create, skip, extend, adjust):

    # create directory if non existing.
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    # specify path for created states.
    path = os.path.join(output_directory, "create.yml")

    # save created states.
    dump(path, create)

    # specify path for skipped states.
    path = os.path.join(output_directory, "skip.yml")

    # save skipped states.
    dump(path, skip)

    # specify path for extended states.
    path = os.path.join(output_directory, "extend.yml")

    # save extended states.
    dump(path, extend)

    # specify path for adjusted states.
    path = os.path.join(output_directory, "adjust.yml")

    # save adjusted states
    dump(path, adjust)


def dump(output_file, tests):
    # configure anchors and aliases for references.
    if not conf_enable_references:
        yaml.Dumper.ignore_aliases = lambda *args: True

    stream = file(output_file, 'a')

    if tests:
        logger.info("Dumping tests to file %s.", output_file)
        yaml.dump(tests, stream, default_flow_style=False)
    else:
        logger.info("No tests to dump.%s", '')

    stream.close()