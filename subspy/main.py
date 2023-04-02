#!/usr/bin/env python3

"""
### Main command line interface for subspy.

Each `subspy` command is mapped to a function which calls the correct
subspy class function. 
"""

import argparse
import atexit
import logging
import re
import sys

import argcomplete
from pysubs2 import make_time

from . import commands
from ._version import __version__
from .exceptions import SubspyException
from .helper import logger_init, set_terminal_title

logger = logging.getLogger(__name__)

################################################################################
# Setup and parse command line arguments
################################################################################


def time(s: str) -> int:
    d = {}
    for v, k in re.findall(r"(\d*\.?\d*)(ms|m|s|h)", s):
        d[k] = float(v)
    return make_time(**d)  # type: ignore  # Argument 1 has incomp. type "**Dict[Any, float]"; expected "Optional[int]"

def command_info(args):
    print("subspy version: {}".format(__version__))
    commands.run_info(args)

def command_chs2cht(args):
    print("subspy version: {}".format(__version__))
    commands.run_chs2cht(args)

def command_rename(args):
    print("subspy version: {}".format(__version__))
    commands.run_rename(args)

def command_srt2ass(args):
    print("subspy version: {}".format(__version__))
    commands.run_srt2ass(args)

def command_trans(args):
    print("subspy version: {}".format(__version__))
    commands.run_trans(args)

def command_shift(args):
    print("subspy version: {}".format(__version__))
    commands.run_shift(args)

def command_dual(args):
    print("subspy version: {}".format(__version__))
    commands.run_dual(args)

def main():
    """
    Read in command line arguments and call the correct command function.
    """

    # Cleanup any title the program may set
    atexit.register(set_terminal_title, "")

    # Create a common parent parser for arguments shared by all subparsers. In
    # practice there are very few of these since subspy supports a range of
    # operations.
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--debug", action="store_true", help="Print additional debugging information"
    )
    parent.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print subspy version and exit",
    )
    parent.add_argument(
        "-i", "--input",
        dest='input',
        help="Open file path",
        default=None,
    )
    parent.add_argument(
        "-o", "--output",
        dest='output',
        help="Save file path",
        default=None,
    )
    parent.add_argument(
        "--in-dir",
        help='Input directory',
        required=False
    )
    parent.add_argument(
        "--out-dir",
        help='Output directory',
        required=False
    )

    # Get the list of arguments before any command
    before_command_args = parent.parse_known_args()

    # The top-level parser object
    parser = argparse.ArgumentParser(parents=[parent])

    # Parser for all conv related commands
    parent_conv = argparse.ArgumentParser(add_help=False)
    parent_conv.add_argument(
        "--mode",
        metavar='MODEL',
        help="srt2ass|ass2srt|chs2cht|cht2chs",
        choices=["srt2ass", "ass2srt", "chs2cht", "cht2chs"],
        default="srt2ass",
    )

    # Parser for all output formatting related flags shared by multiple
    # commands.
    parent_format = argparse.ArgumentParser(add_help=False)
    parent_format.add_argument(
        "-f", "-r",
        "--from", "--read",
        dest='in_format',
        metavar='FORMAT',
        help="srt|ass",
        choices=["srt", "ass"],
        default=None,
    )
    parent_format.add_argument(
        "-t", "-w",
        "--to", "--write",
        dest='out_format',
        metavar='FORMAT',
        help="srt|ass",
        choices=["srt", "ass"],
        default=None,
    )
    parent_format.add_argument(
        "--in-lang",
        default=None,
    )
    parent_format.add_argument(
        "--out-lang",
        default=None,
    )

    # for srt2ass
    parent_srt2ass = argparse.ArgumentParser(add_help=False)
    parent_srt2ass.add_argument(
        "--ass-style",
        default=None,
    )
    parent_srt2ass.add_argument(
        "--ass-style-mode",
        help="merge|builtin|new",
        choices=["merge", "builtin", "new"],
        default='merge',
    )
    parent_srt2ass.add_argument(
        "--video-type",
        help="movie|tv",
        choices=["movie", "tv"],
        default='tv',
    )

    # for trans
    parent_trans = argparse.ArgumentParser(add_help=False)
    parent_trans.add_argument(
        "--trans-engine",
        default='bing',
    )
    parent_trans.add_argument(
        "--both",
        help="Save both subs file",
        action="store_true",
    )

    # Parser for all rename related commands
    parent_rename = argparse.ArgumentParser(add_help=False)
    parent_rename.add_argument(
        "--name",
        help="Provided the series name.",
        #default=None,
    )
    parent_rename.add_argument(
        "--new-style",
        help="Create filename style.",
        #default=None,
    )
    parent_rename.add_argument(
        "--name-pattern",
        help="Origin filename pattern.",
        #default=None,
    )
    parent_rename.add_argument(
        "--exclude",
        help="Exclude files.",
        default=None,
    )

    # Parser for all shift related commands
    parent_shift = argparse.ArgumentParser(add_help=False)
    parent_shift.add_argument(
        "--back",
        metavar="TIME", type=time,
        help="Delay all subtitles by given time amount. Time is specified like this: '1m30s', '0.5s', ..."
    )
    parent_shift.add_argument(
        "--forward",
        metavar="TIME", type=time,
        help="The opposite of --shift (subtitles will appear sooner)."
    )

    # Parser for all bilingual related commands
    parent_dual = argparse.ArgumentParser(add_help=False)
    parent_dual.add_argument(
        "--top",
        metavar="Top srt file",
        help="Top bilingual subtitles."
    )
    parent_dual.add_argument(
        "--bot",
        metavar="Bot srt file",
        help="Bot bilingual subtitles."
    )

    # Support multiple commands for this tool
    subparser = parser.add_subparsers(title="Commands", metavar="")

    # Command Groups
    #
    # Python argparse doesn't support grouping commands in subparsers as of
    # January 2021 :(. The best we can do now is order them logically.

    chs2cht = subparser.add_parser(
        "chs2cht",
        parents=[parent, parent_conv, parent_format],
        help="Convert simplified chinese to traditional chinese or vice versa",
    )
    chs2cht.set_defaults(func=command_chs2cht)

    srt2ass = subparser.add_parser(
        "srt2ass",
        parents=[parent, parent_conv, parent_format, parent_srt2ass],
        help="Convert files to .ass from .srt or vice versa",
    )
    srt2ass.set_defaults(func=command_srt2ass)

    trans = subparser.add_parser(
        "trans",
        parents=[parent, parent_trans, parent_format],
        help="Translate to your language",
    )
    trans.set_defaults(func=command_trans)

    rename = subparser.add_parser(
        "rename",
        parents=[parent, parent_rename, parent_format],
        help="Rename the provided file",
    )
    rename.set_defaults(func=command_rename)

    shift = subparser.add_parser(
        "shift",
        parents=[parent, parent_shift, parent_format],
        help="Shift time of the provided file",
    )
    shift.set_defaults(func=command_shift)

    dual = subparser.add_parser(
        "dual",
        parents=[parent, parent_dual, parent_format],
        help="Creating top/bottom bilingual subtitles",
    )
    dual.set_defaults(func=command_dual)

    argcomplete.autocomplete(parser)
    args, unknown_args = parser.parse_known_args()

    # Warn about unknown arguments, suggest subspy update.
    if len(unknown_args) > 0:
        logger.warning(
            "Unknown arguments passed. You may need to update subspy.")
        for unknown_arg in unknown_args:
            logger.warning('Unknown argument "{}"'.format(unknown_arg))

    # Concat the args before the command with those that were specified
    # after the command. This is a workaround because for some reason python
    # won't parse a set of parent options before the "command" option
    # (or it is getting overwritten).
    for key, value in vars(before_command_args[0]).items():
        if getattr(args, key) != value:
            setattr(args, key, value)

    logger_init(args)

    # Handle deprecated arguments.

    if hasattr(args, "func"):
        try:
            args.func(args)
        except SubspyException as e:
            logger.error(e)
            sys.exit(1)
    else:
        logger.error("Missing Command.\n")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
