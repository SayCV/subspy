"""

"""

import argparse
import dataclasses
import logging
import sys
from pathlib import Path as path
from pprint import pprint

import pysubs2
from opencc import OpenCC

from subspy.helpers import SUBSPY_ROOT, abbreviate_language
from subspy.translator import SubspyTranslator

from .exceptions import SubspyException
from .util import guess_encoding, guess_lang, filename_is_regex

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

# subspy conv --in-dir data --out-dir test --mode ass2srt --ass-style 1 --ass-style-mode builtin
def run_srt2ass(args):
    #parser = argparse.ArgumentParser()
    #args = parser.parse_args()
    if args.input is None and args.in_dir is None:
        logger.error("No input file found")
        sys.exit(1)

    if args.in_dir is None:
        input_dir = path.cwd()
    else:
        input_dir = path(args.in_dir)

    if args.out_dir is None:
        output_dir = path(args.in_dir)
    else:
        output_dir = path(args.out_dir)

    in_format = "ass" if args.mode == 'ass2srt' else args.in_format
    in_format = "srt" if args.mode == 'srt2ass' else in_format
    if in_format is None:
        logger.error("No input format found")
        sys.exit(1)

    out_format = args.out_format
    if out_format is None:
        out_format = "srt" if args.mode == 'ass2srt' else "ass"

    in_files = []
    if input_dir is not None:
        for _file in input_dir.glob(f"*.{in_format}"):
            in_file: path = input_dir / _file.name
            if in_file.is_file():
                in_files.append(in_file)
    else:
        in_files = [path(in_file).absolute()]

    if in_files:
        for _file in in_files:
            _in_file = _file
            out_file = output_dir / _file.name
            out_file = out_file.with_suffix(f".{out_format}")
            subs = pysubs2.load(_in_file, encoding=guess_encoding(_in_file))
            if args.mode == 'srt2ass' and args.ass_style is not None:
                new_style_file = path(args.ass_style)
                if args.ass_style_mode == "builtin":
                    n = int(args.ass_style)
                    assert n<10 and n>0
                    new_style_file = path(SUBSPY_ROOT / 'styles' / f'style_sample{n}.ass')
                new_subs_style = pysubs2.load(new_style_file, encoding=guess_encoding(new_style_file))

                if args.ass_style_mode == "merge":
                    subs.import_styles(new_subs_style)
                else:
                    #subs.style = {"Default": pysubs2.SSAStyle.DEFAULT_STYLE.copy()}
                    subs.styles = new_subs_style.styles.copy()

            #for style in subs.styles:
            #    val = subs.styles[style]
            #    pprint({field.name: getattr(val, field.name) for field in dataclasses.fields(val)})
            #    pprint(val)
            subs.save(out_file, format_=out_format)
            logger.info(f"Processed {out_file} done.")
    else:
        logger.info(f'Not found **.{in_format} in {input_dir}.')

# subspy trans --in-dir data --input *.eng.srt --output *.chs.srt --trans-engine=youdao
def run_trans(args):
    if args.input is None and args.in_dir is None:
        logger.error("Please provide input file!")
        sys.exit(1)
    input = path(args.input).absolute()
    #if not input.exists() and args.in_dir is None:
    #    logger.error("Input file non exist")
    #    sys.exit(1)

    if args.output is None and args.out_dir is None:
        logger.error("Please provide output file!")
        sys.exit(1)
    output = path(args.output).absolute()

    in_format = args.in_format
    if in_format is None:
        in_format = input.suffix.lstrip('.')
    if in_format is None:
        logger.error("No input format found")
        sys.exit(1)

    out_format = args.out_format
    if out_format is None:
        out_format = in_format

    if args.in_dir is None:
        input_dir = path.cwd()
    else:
        input_dir = path(args.in_dir)

    if args.out_dir is None:
        output_dir = path(args.in_dir)
    else:
        output_dir = path(args.out_dir)

    in_lang = args.in_lang
    if in_lang is None:
        in_lang = guess_lang(input.name)
    if in_lang is None:
        in_lang = guess_lang(args.in_format)

    out_lang = args.out_lang
    if out_lang is None:
        out_lang = guess_lang(output.name)
    if in_lang is None:
        out_lang = guess_lang(args.out_format)

    assert in_lang is not None
    assert out_lang is not None

    in_files = []
    if input_dir is not None and filename_is_regex(args.input):
        for _file in input_dir.glob(f"*.{in_lang}.{in_format}"):
            in_file: path = input_dir / _file.name
            if in_file.is_file():
                in_files.append(in_file)
    else:
        in_files = [input]

    if in_files:
        for _file in in_files:
            if output is None:
                if in_lang is None:
                    output = input.parent / input.with_suffix(f".{out_lang}.{out_format}")
                else:
                    output = input.parent / path(input.stem).with_suffix(f".{out_lang}.{out_format}")

            out_file = output
            if filename_is_regex(out_file):
                out_file = output_dir / path(_file.name.replace(f".{in_lang}.{in_format}", f".{out_lang}.{out_format}"))
            #data: str = _file.read_text(encoding=guess_encoding(_file), errors='ignore')
            #if not data:
            #    raise SubspyException(f"File `{input}` is empty")
            #query_text: str = data
            # TODO -> Avoid the length of `query_text` exceeds the limit.

            text_list = []
            subs = pysubs2.load(_file, encoding=guess_encoding(_file))
            for event in subs.events:
                text_list.append(event.plaintext.replace('\n', ' '))

            sts = SubspyTranslator()

            translator: str = args.trans_engine
            from_language: str = abbreviate_language(in_lang, engine = '')
            to_language: str = abbreviate_language(out_lang, engine = '')

            translated_sen = sts.translate(text_list, translator, from_language, to_language)
            translated_sen_list = translated_sen.split('\n')

            if len(text_list) == len(translated_sen_list):
                for i in range(len(text_list)):
                    subs.events[i].plaintext = translated_sen_list[i]
            else:
                raise SubspyException(f"The length translated sen list is error")

            out_file.parent.mkdir(exist_ok=True)
            subs.save(out_file, format_=out_format)
            logger.info(f"Processed {out_file} done.")

            if args.both:
                out_file = out_file.parent / out_file.name.replace(f".{out_lang}.{out_format}", f".{out_lang}+{in_lang}.{out_format}")
                for i in range(len(text_list)):
                    subs.events[i].plaintext = '\n'.join([translated_sen_list[i], text_list[i]])
                out_file.parent.mkdir(exist_ok=True)
                subs.save(out_file, format_=out_format)
                logger.info(f"Processed {out_file} done.")
    else:
        logger.info(f'Not found *.{in_lang}.{in_format} in {input_dir}.')

# subspy rename --in-dir data
def run_rename(args):
    logger.info(f"Rename Command Unimplemented!")
