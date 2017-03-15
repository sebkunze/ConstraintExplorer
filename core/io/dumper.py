import yaml

from core.utils            import logger

conf_enable_references = False

def dump(tests, output_file):
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