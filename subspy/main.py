#!/usr/bin/env python3

"""
### Main command line interface for subspy.

Each `subspy` command is mapped to a function which calls the correct
subspy class function. 
"""

import argparse
import atexit
import functools
import logging
import sys

import argcomplete

from . import commands, helpers
from ._version import __version__
from .exceptions import SubspyException

logger = logging.getLogger(__name__)

################################################################################
# Setup and parse command line arguments
################################################################################


def command_info(args):
    print("subspy version: {}".format(__version__))
    commands.run_info(args)

def command_chs2cht(args):
    print("subspy version: {}".format(__version__))
    commands.run_chs2cht(args)

def command_rename(args):
    print("subspy version: {}".format(__version__))
    commands.run_rename(args)

def main():
    """
    Read in command line arguments and call the correct command function.
    """

    # Cleanup any title the program may set
    atexit.register(helpers.set_terminal_title, "")

    # Setup logging for displaying background information to the user.
    logging.basicConfig(
        style="{", format="[{levelname:<7}] {message}", level=logging.INFO
    )
    # Add a custom status level for logging what subspy is doing.
    logging.addLevelName(25, "STATUS")
    logging.Logger.status = functools.partialmethod(logging.Logger.log, 25)
    logging.status = functools.partial(logging.log, 25)

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

    # Get the list of arguments before any command
    before_command_args = parent.parse_known_args()

    # The top-level parser object
    parser = argparse.ArgumentParser(parents=[parent])

    # Parser for all rename related commands
    parent_rename = argparse.ArgumentParser(add_help=False)
    parent_rename.add_argument(
        "--name-style",
        help="Create filename style.",
    )

    # Parser for all chs<->cht related commands
    parent_chs2cht = argparse.ArgumentParser(add_help=False)
    parent_chs2cht.add_argument(
        "--chs2cht-mode",
        help="chs2cht|cht2chs",
        choices=["chs2cht", "cht2chs"],
        default="chs2cht",
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

    # Support multiple commands for this tool
    subparser = parser.add_subparsers(title="Commands", metavar="")

    # Command Groups
    #
    # Python argparse doesn't support grouping commands in subparsers as of
    # January 2021 :(. The best we can do now is order them logically.

    chs2cht = subparser.add_parser(
        "chs2cht",
        parents=[parent, parent_chs2cht, parent_format],
        help="chs2cht",
    )
    chs2cht.set_defaults(func=command_chs2cht)

    rename = subparser.add_parser(
        "rename",
        parents=[parent, parent_rename, parent_format],
        help="Rename the provided file",
    )
    rename.set_defaults(func=command_rename)

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

    # Change logging level if `--debug` was supplied.
    if args.debug:
        logging.getLogger("").setLevel(logging.DEBUG)

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
