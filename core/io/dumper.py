import yaml

from core.utils import logger

enable_references = False

def dump(tests, output_file):
    # configure anchors and aliases for references.
    if not enable_references:
        yaml.Dumper.ignore_aliases = lambda *args: True

    stream = file(output_file, 'a')

    if tests:
        logger.info("Dumping tests to file %s", output_file)
        yaml.dump_all(tests, stream)
    else:
        raise ValueError("Empty list!")

    stream.close()