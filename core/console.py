from optparse import Option


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

def populate_option_parser(parser):
    parser.add_option("-i", "--input-files",
                      action="extend",
                      dest="inputs",
                      metavar="FILE",
                      help="specified comma separated list of input FILES")

    parser.add_option("-o", "--output_file",
                      action="extend",
                      dest="output",
                      metavar="FILE",
                      help="defined output to FILE")

    parser.add_option("-q", "--quiet",
                      action="store_false",
                      dest="verbose",
                      default=True,
                      help="do print status messages to stdout")

    parser.add_option("-v", "--verbose",
                      action="store_true",
                      dest="verbose",
                      default=False,
                      help="do not print status messages to stdout")

    return parser