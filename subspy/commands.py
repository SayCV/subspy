"""

"""

import logging
import sys
from pathlib import Path as path

from opencc import OpenCC

from .exceptions import SubspyException
from .util import guess_encoding, guess_lang

logger = logging.getLogger(__name__)

def run_info(args):
    logger.info(f"Info Command Unimplemented!")

def run_chs2cht(args):
    if args.input is None:
        logger.error("Please provide input file!")
        sys.exit(1)
    input = path(args.input).absolute()
    if not input.exists():
        logger.error("Input file non exist")
        sys.exit(1)

    in_format = args.in_format
    if in_format is None:
        in_format = input.suffix.lstrip('.')
    if in_format is None:
        logger.error("No input format found")
        sys.exit(1)

    out_format = args.out_format
    if out_format is None:
        out_format = in_format

    in_lang = args.in_lang
    if in_lang is None:
        in_lang = guess_lang(input.name)

    out_lang = args.out_lang
    if out_lang is None:
        if in_lang is None:
            out_lang = "cht" if args.mode == 'chs2cht' else "chs"
        elif "chs" in in_lang and args.mode == 'chs2cht':
            out_lang = in_lang.replace('chs', 'cht')
        elif "cht" in in_lang and args.mode == 'cht2chs':
            out_lang = in_lang.replace('cht', 'chs')
        elif "\u7B80" in in_lang and args.mode == 'chs2cht':
            out_lang = in_lang.replace('\u7B80', '\u7E41')
        elif "\u7E41" in in_lang and args.mode == 'cht2chs':
            out_lang = in_lang.replace('\u7E41', '\u7B80')
        else:
            out_lang = "cht" if args.mode == 'chs2cht' else "chs"

    output = args.output
    if output is None:
        if in_lang is None:
            output = input.parent / input.with_suffix(f".{out_lang}.{out_format}")
        else:
            output = input.parent / path(input.stem).with_suffix(f".{out_lang}.{out_format}")

    data: str = input.read_text(encoding=guess_encoding(input), errors='ignore')
    if not data:
        raise SubspyException(f"File `{input}` is empty")
 
    cc = OpenCC()
    if args.mode == 'chs2cht':
        cc.set_conversion('s2twp')
    else:
        cc.set_conversion('tw2sp')
    result = cc.convert(data)

    out_file = path(output)
    out_file.parent.mkdir(exist_ok=True)
    out_file.write_text(result)
    logger.info(f'{out_file} done.')

def run_rename(args):
    logger.info(f"Rename Command Unimplemented!")
