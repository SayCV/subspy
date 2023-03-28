"""

"""

import logging
import sys
from pathlib import Path as path

import pysubs2
from opencc import OpenCC

from subspy import rename
from subspy.helpers import (SUBSPY_ROOT, abbreviate_language,
                            auto_add_fontsize_to_subs_textline)

from .exceptions import SubspyException
from .util import filename_is_regex, guess_encoding, guess_lang

logger = logging.getLogger(__name__)

def run_info(args):
    logger.info(f"Info Command Unimplemented!")

def run_chs2cht(args):
    logger.info(f"Chs2cht Command Starting...")
    if args.input is None and args.in_dir is None:
        logger.error("Please provide input file!")
        sys.exit(1)
    input = path(args.input).absolute()

    #if args.output is None and args.out_dir is None:
    #    logger.error("Please provide output file!")
    #    sys.exit(1)
    output = path(args.output).absolute() if args.output is not None else None

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
            if in_lang is None:
                output = _file.parent / _file.with_suffix(f".{out_lang}.{out_format}")
            else:
                output = _file.parent / path(_file.stem).with_suffix(f".{out_lang}.{out_format}")

            out_file = output
            if filename_is_regex(out_file):
                out_file = output_dir / path(_file.name.replace(f".{in_lang}.{in_format}", f".{out_lang}.{out_format}"))
            
            data: str = _file.read_text(encoding=guess_encoding(_file), errors='ignore')
            if not data:
                raise SubspyException(f"File `{_file}` is empty")

            cc = OpenCC()
            if args.mode == 'chs2cht':
                cc.set_conversion('s2twp')
            else:
                cc.set_conversion('tw2sp')
            result = cc.convert(data)

            out_file = path(output)
            out_file.parent.mkdir(exist_ok=True)
            out_file.write_text(result, encoding='utf-8', errors='ignore')
            logger.info(f"Processed {out_file} done.")
    else:
        logger.info(f'Not found *.{in_lang}.{in_format} in {input_dir}.')

# subspy srt2ass --in-dir data --out-dir test --mode ass2srt --ass-style 1 --ass-style-mode builtin
def run_srt2ass(args):
    logger.info(f"Srt2ass Command Starting...")
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
            data: str = _in_file.read_text(encoding=guess_encoding(_file), errors='ignore')
            subs = pysubs2.SSAFile.from_string(data)
            # subs = pysubs2.load(_in_file, encoding=guess_encoding(_in_file), errors='ignore')
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
                subs.info = new_subs_style.info.copy()

            #for style in subs.styles:
            #    val = subs.styles[style]
            #    pprint({field.name: getattr(val, field.name) for field in dataclasses.fields(val)})
            #    pprint(val)
            subs.save(out_file, format_=out_format)
            logger.info(f"Processed {out_file} done.")

            data: str = out_file.read_text(encoding=guess_encoding(out_file), errors='ignore')
            in_lang = guess_lang(_in_file.name)
            if in_lang:
                dual_lang = in_lang.split('+')
                if len(dual_lang) == 2:
                    logger.info(f"Detected dual language: {in_lang}.")
                    lines = []
                    for line in data.split('\n'):
                        lines.append(line.replace('\\N', "\\N{" + r'\r' + f"{dual_lang[1].upper()}" + "}"))
                    out_file.write_text('\n'.join(lines), encoding=guess_encoding(out_file), errors='ignore')
                subs_fixed = pysubs2.load(out_file, encoding=guess_encoding(out_file))
                for event in subs_fixed.events:
                    if '\\N' in event.text:
                        text = event.text.split('\\N')
                        fs = auto_add_fontsize_to_subs_textline(text[0], args.video_type)
                        if fs > 0:
                            text0 = r"{\fs%d}%s" % (fs, text[0])
                            event.text = '\\N'.join([text0, text[1]])
                subs_fixed.save(out_file, format_=out_format)
                logger.info(f"Post processed {out_file} done.")
    else:
        logger.info(f'Not found **.{in_format} in {input_dir}.')

# subspy trans --in-dir data --input *.eng.srt --output *.chs.srt --trans-engine=youdao
def run_trans(args):
    logger.info(f"Trans Command Starting...")
    if args.input is None and args.in_dir is None:
        logger.error("Please provide input file!")
        sys.exit(1)
    input = path(args.input).absolute()
    #if not input.exists() and args.in_dir is None:
    #    logger.error("Input file non exist")
    #    sys.exit(1)

    #if args.output is None and args.out_dir is None:
    #    logger.error("Please provide output file!")
    #    sys.exit(1)
    #output = path(args.output).absolute()

    in_format = args.in_format
    if in_format is None:
        in_format = input.suffix.lstrip('.')
    if in_format is None:
        logger.error("No input format found")
        sys.exit(1)

    out_format = args.out_format
    if out_format is None:
        out_format = in_format

    input_dir = path.cwd() if args.in_dir is None else path(args.in_dir)
    output_dir = path(args.in_dir) if args.out_dir is None else path(args.out_dir)

    in_lang = args.in_lang
    if in_lang is None:
        in_lang = guess_lang(input.name)
    if in_lang is None:
        in_lang = guess_lang(args.in_format)

    out_lang = args.out_lang
    if out_lang is None:
        out_lang = guess_lang(output.name)
    if out_lang is None:
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
            if in_lang is None:
                output = _file.parent / _file.with_suffix(f".{out_lang}.{out_format}")
            else:
                output = _file.parent / path(_file.stem).with_suffix(f".{out_lang}.{out_format}")

            out_file = output
            if filename_is_regex(out_file):
                out_file = output_dir / path(_file.name.replace(f".{in_lang}.{in_format}", f".{out_lang}.{out_format}"))
            #data: str = _file.read_text(encoding=guess_encoding(_file), errors='ignore')
            #if not data:
            #    raise SubspyException(f"File `{input}` is empty")
            #query_text: str = data
            # TODO -> Avoid the length of `query_text` exceeds the limit.

            text_list = []
            data: str = _file.read_text(encoding=guess_encoding(_file), errors='ignore')
            subs = pysubs2.SSAFile.from_string(data)
            #subs = pysubs2.load(_file, encoding=guess_encoding(_file))
            both_subs = pysubs2.SSAFile.from_string(data) if args.both else None
            for event in subs.events:
                text_list.append(event.plaintext.replace('\n', ' '))

            from subspy.translator import SubspyTranslator
            sts = SubspyTranslator()

            translator: str = args.trans_engine
            from_language: str = abbreviate_language(in_lang, engine = '')
            to_language: str = abbreviate_language(out_lang, engine = '')

            translated_sen = sts.translate(text_list, translator, from_language, to_language)
            translated_sen_list = translated_sen.split('\n')

            if len(text_list) == len(translated_sen_list):
                for i in range(len(text_list)):
                    subs.events[i].plaintext = translated_sen_list[i]
                    if both_subs and out_format == 'srt':
                        both_subs.events[i].plaintext = f"{translated_sen_list[i]}\n{text_list[i]}"
            else:
                raise SubspyException(f"The length translated sen list is error")

            out_file.parent.mkdir(exist_ok=True)
            subs.save(out_file, format_=out_format)
            logger.info(f"Processed {out_file} done.")

            if both_subs and out_format == 'srt':
                both_out_file = output_dir / path(out_file.name.replace(f".{out_lang}.{out_format}", f".{out_lang}+{in_lang}.{out_format}"))
                both_out_file.parent.mkdir(exist_ok=True)
                both_subs.save(both_out_file, format_=out_format)
                logger.info(f"Processed {both_out_file} done.")
    else:
        logger.info(f'Not found *.{in_lang}.{in_format} in {input_dir}.')

# subspy rename --in-dir data
def run_rename(args):
    logger.info(f"Rename Command Starting...")
    video_dir: path = None
    subs_dir: path = None

    if args.in_dir:
        video_dir = path(args.in_dir)
        subs_dir = video_dir / 'subs'

    if video_dir is None:
        video_dir = path('videos')
    if subs_dir is None:
        subs_dir = path('subs')

    rename.run(args, video_dir, subs_dir)
    logger.info(f'Rename files done.')

def run_shift(args):
    logger.info(f"Shift Command Starting...")
    if args.input is None and args.in_dir is None:
        logger.error("Please provide input file!")
        sys.exit(1)
    input = path(args.input).absolute()

    in_format = args.in_format
    if in_format is None:
        in_format = input.suffix.lstrip('.')
    if in_format is None:
        logger.error("No input format found")
        sys.exit(1)

    out_format = args.out_format
    if out_format is None:
        out_format = in_format

    input_dir = path.cwd() if args.in_dir is None else path(args.in_dir)
    output_dir = path(args.in_dir) if args.out_dir is None else path(args.out_dir)

    in_files = []
    if input_dir is not None and filename_is_regex(args.input):
        for _file in input_dir.glob(f"*.{in_format}"):
            in_file: path = input_dir / _file.name
            if in_file.is_file():
                in_files.append(in_file)
    else:
        in_files = [input]

    if in_files:
        for _file in in_files:
            output = _file.parent / _file.with_suffix(f".{out_format}")

            out_file = output
            if filename_is_regex(out_file):
                out_file = output_dir / path(_file.name.replace(f".{in_format}", f".{out_format}"))

            data: str = _file.read_text(encoding=guess_encoding(_file), errors='ignore')
            subs = pysubs2.SSAFile.from_string(data)
            #subs = pysubs2.load(_file, encoding=guess_encoding(_file))

            if args.forward is not None:
                subs.shift(ms=args.forward)
                logger.info(f"Processed forward {args.forward} to {out_file} done.")
            elif args.back is not None:
                subs.shift(ms=-args.back)
                logger.info(f"Processed back {args.back} to {out_file} done.")

            out_file.parent.mkdir(exist_ok=True)
            subs.save(out_file, format_=out_format)
            logger.info(f"Processed {out_file} done.")
    else:
        logger.info(f'Not found *.{in_format} in {input_dir}.')
