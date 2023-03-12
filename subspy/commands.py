"""

"""

import logging
import sys
from pathlib import Path as path

from opencc import OpenCC

from .exceptions import SubspyException
from .util import get_encoding

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

    output = args.output
    if output is None:
        in_lang = path(input.stem).suffix.lstrip('.')
        if in_lang is None:
            output = input.parent / input.with_suffix(f".cht.{out_format}" if args.chs2cht_mode == 'chs2cht' else f".chs.{out_format}")
        elif "chs" in in_lang:
            in_lang = in_lang.replace('chs', 'cht')
            output = input.parent / path(input.stem).with_suffix(f".{in_lang}.{out_format}")
        elif "cht" in in_lang:
            in_lang = in_lang.replace('cht', 'chs')
            output = input.parent / path(input.stem).with_suffix(f".{in_lang}.{out_format}")
        else:
            output = input.parent / input.with_suffix(f".cht.{out_format}" if args.chs2cht_mode == 'chs2cht' else f".chs.{out_format}")

    data: str = input.read_text(encoding=get_encoding(input), errors='ignore')
    if not data:
        raise SubspyException(f"File `{input}` is empty")
 
    cc = OpenCC()
    if args.chs2cht_mode == 'chs2cht':
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
