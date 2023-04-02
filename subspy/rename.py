"""
"""

import logging
import mimetypes
import os
import re
import sys
from pathlib import Path as path
from pprint import pprint
from typing import Dict, List

from .helper import count_characters_chinese_english_by_file
from .util import guess_lang

logger = logging.getLogger(__name__)

filename_delims = '.- '

default_filename_pattern = r"(?P<p_video_name>.*)[\.\- ]?[sS]*(?P<p_video_season>\d\d)[\.\- ]?[eE]*(?P<p_video_episode>\d\d)[\.\- ]?(?P<p_video_episode_name>[, \^:^!\w.\-\'\(\)]*)[\.\- ]?(?P<p_video_extra>\d{3,5}p.*)"

default_filename_style = r"@VIDEO_NAME@.@VIDEO_SEASON@@VIDEO_EPISODE@.@VIDEO_EPISODE_NAME@.@VIDEO_EXTRA@"


def is_video_file(fullpath: path):
    mimetype, _ = mimetypes.guess_type('file://%s' % fullpath)
    if mimetype:
        category = mimetype.split('/')[0]
        return category == 'video'
    return False


def find_video_files(directory: path, recursive=False):
    results = []

    if recursive:
        for dirpath, dirnames, filenames in path.walk(directory, topdown=False):
            for name in filenames:
                fullpath = name  # dirpath / name
                if is_video_file(fullpath):
                    results.append(fullpath)
    else:
        for entry in directory.iterdir():
            fullpath = entry  # directory / entry
            if fullpath.is_file() and is_video_file(fullpath):
                results.append(fullpath)

    return sorted(results)


def is_subtitle_file(fullpath: path):
    if fullpath.exists():
        return fullpath.suffix == '.ass' or fullpath.suffix == '.smi' or fullpath.suffix == '.srt' or fullpath.suffix == '.ssa' or fullpath.suffix == '.vtt'
    return False


def find_subtitle_files(directory: path, recursive=False):
    results = []

    if recursive:
        for dirpath, dirnames, filenames in path.walk(directory, topdown=False):
            for name in filenames:
                fullpath = name  # dirpath / name
                if is_subtitle_file(fullpath):
                    results.append(fullpath)
    else:
        for entry in directory.iterdir():
            fullpath = entry  # directory / entry
            if fullpath.is_file() and is_subtitle_file(fullpath):
                results.append(fullpath)

    return sorted(results)


def _guess_media_filename_fields(filename: path, pattern=None):
    logger.debug(f'Processing: {filename.name}')
    pattern = default_filename_pattern if pattern is None else pattern
    env_pattern = os.environ.get('TVS_FILENAME_PATTERN')
    if env_pattern:
        pattern = env_pattern
    logger.debug(f'Used pattern: {pattern}')

    regex = re.compile(pattern)
    matched = regex.match(filename.name)
    if matched is None:
        logger.error(f'Failed to guess fields: {filename}\n')
        sys.exit(1)

    _fields = matched.groupdict()

    video_name = _fields[u'p_video_name']
    video_season = _fields[u'p_video_season']
    video_episode = _fields[u'p_video_episode']
    if u'p_video_episode_name' in _fields:
        video_episode_name = _fields[u'p_video_episode_name'].rstrip('.')
    else:
        video_episode_name = None
    if u'p_video_extra' in _fields:
        video_extra = _fields[u'p_video_extra']
    else:
        video_extra = None

    logger.debug(
        f'Succeeded to guess fields: {video_name},{video_season},{video_episode},{video_episode_name},{video_extra}')
    return (video_name, video_season, video_episode, video_episode_name, video_extra)


def guess_fields_from_videos(directory: path, recursive=False):
    results = []
    video_files = find_video_files(directory, recursive=False)

    for filename in video_files:
        #_, video_season, video_episode, video_episode_name, video_extra = _guess_media_filename_fields(filename)
        results.append(_guess_media_filename_fields(filename))
    return results


def guess_fields_from_subtitles(directory: path, recursive=False):
    results = []
    subs_files = find_subtitle_files(directory, recursive=False)

    for filename in subs_files:
        video_name, video_season, video_episode, video_episode_name, video_extra = _guess_media_filename_fields(
            filename)
        results.append((video_name, video_season, video_episode, video_episode_name, video_extra,
                       guess_lang_from_subtitle(filename)))
    return results

def guess_lang_from_subtitle(filename: path):
    results = None

    in_lang = guess_lang(filename.name)
    if in_lang is None:
        en_count, zh_cn_count, zh_tw_count = count_characters_chinese_english_by_file(
            filename)
        lang = []
        if zh_tw_count > 100:
            lang.append('cht')
        elif zh_cn_count > 500:
            lang.append('chs')

        if en_count > 500:
            lang.append('eng')
        results = '+'.join(lang)
    else:
        results = in_lang
    return results

def guess_lang_from_subtitles(directory: path, recursive=False):
    results = []
    subs_files = find_subtitle_files(directory, recursive=False)

    for filename in subs_files:
        lang = guess_lang_from_subtitle(filename)
        results.append(lang)
    return results

class video_series:

    class episode:

        class eps_lang:

            def __init__(self):
                self.eng = None
                self.chs = None
                self.chs_eng = None
                self.cht_eng = None

            def set_eng(self, eng):
                self.eng = eng

            def set_chs(self, chs):
                self.chs = chs

            def set_chs_eng(self, chs_eng):
                self.chs_eng = chs_eng

            def set_cht_eng(self, cht_eng):
                self.cht_eng = cht_eng

        def __init__(self, number, name, extra):
            self.number = number
            self.name = name
            self.extra = extra
            self.srt = self.eps_lang()
            self.ass = self.eps_lang()

        def __str__(self):
            return ','.join(self.number, self.name, self.extra)

    def __init__(self, args):
        self.args = args
        if self.args.name_pattern:
            self.origin_style = self.args.name_pattern
        else:
            self.origin_style = default_filename_pattern
        if self.args.new_style:
            self.new_style = self.args.new_style
        else:
            self.new_style = default_filename_style
        self.video_name = None
        self.video_season = None
        self.video_episode: Dict(str, self.episode) = {}

    def __str__(self):
        return ','.join([self.video_name, self.video_season])


def run(args, video_dir: path, subs_dir: path, recursive=False):
    clz = video_series(args)

    list_fields_from_videos = guess_fields_from_videos(video_dir)
    list_fields_from_subtitles = guess_fields_from_subtitles(subs_dir)
    # pprint(list_fields_from_video)
    # pprint(list_fields_from_subtitle)
    # list_lang_from_subtitle = guess_lang_from_subtitles(subs_dir)
    # pprint(list_lang_from_subtitle)

    for list_fields in list_fields_from_videos:
        if len(list_fields) != 5:
            logger.error(
                f'Detected error length of fields {len(list_fields)} expected 5 at {__file__} line {sys._getframe().f_lineno}\n')
            sys.exit(1)

        if clz.video_name is None:
            clz.video_name = list_fields[0]
        elif clz.video_name != list_fields[0]:
            logger.warning(
                f'Detected conflict video name `{list_fields[0]}` expected `{clz.video_name}` at {__file__} line {sys._getframe().f_lineno}\n')

        if clz.video_season is None:
            clz.video_season = list_fields[1]
        elif clz.video_season != list_fields[1]:
            logger.warning(
                f'Detected conflict video name `{list_fields[1]}` expected `{clz.video_season}` at {__file__} line {sys._getframe().f_lineno}\n')

        video_episode = list_fields[2]
        video_episode_name = list_fields[3]
        _video_extra = path(list_fields[4])
        video_extra = _video_extra.stem.rstrip('.')
        if video_episode not in clz.video_episode:
            clz.video_episode[video_episode] = clz.episode(
                video_episode, video_episode_name, video_extra)

    for list_fields in list_fields_from_subtitles:
        if len(list_fields) != 6:
            logger.error(
                f'Detected error length of fields {len(list_fields)} expected 6 at {__file__} line {sys._getframe().f_lineno}\n')
            sys.exit(1)

        if clz.video_name is None:
            clz.video_name = list_fields[0]
        elif clz.video_name != list_fields[0]:
            logger.warning(
                f'Detected conflict video name `{list_fields[0]}` expected `{clz.video_name}` at {__file__} line {sys._getframe().f_lineno}\n')

        if clz.video_season is None:
            clz.video_season = list_fields[1]
        elif clz.video_season != list_fields[1]:
            logger.warning(
                f'Detected conflict video name `{list_fields[1]}` expected `{clz.video_season}` at {__file__} line {sys._getframe().f_lineno}\n')

        def _set_eps_lang(filename: path):
            if video_suffix in '.srt':
                if in_lang == 'eng':
                    clz.video_episode[video_episode].srt.eng = filename
                elif in_lang == 'chs':
                    clz.video_episode[video_episode].srt.chs = filename
                elif in_lang == 'cht':
                    clz.video_episode[video_episode].srt.cht = filename
                elif in_lang == 'chs+eng':
                    clz.video_episode[video_episode].srt.chs_eng = filename
                elif in_lang == 'cht+eng':
                    clz.video_episode[video_episode].srt.cht_eng = filename
            elif video_suffix in '.ass':
                if in_lang == 'eng':
                    clz.video_episode[video_episode].ass.eng = filename
                elif in_lang == 'chs':
                    clz.video_episode[video_episode].ass.chs = filename
                elif in_lang == 'cht':
                    clz.video_episode[video_episode].ass.cht = filename
                elif in_lang == 'chs+eng':
                    clz.video_episode[video_episode].ass.chs_eng = filename
                elif in_lang == 'cht+eng':
                    clz.video_episode[video_episode].ass.cht_eng = filename

        video_episode: str = list_fields[2]
        video_episode_name = list_fields[3]
        _video_extra = path(list_fields[4])
        video_extra = _video_extra.stem.strip('.')
        video_suffix = _video_extra.suffix
        in_lang = list_fields[5]
        _filename = '.'.join([list_fields[0], 'S' + list_fields[1] +
                             'E' + video_episode, video_extra, video_suffix.strip('.')])
        if video_episode_name != '':
            _filename = '.'.join([list_fields[0], 'S' + list_fields[1] + 'E' +
                                 video_episode, video_episode_name, video_extra, video_suffix.strip('.')])
            if video_episode in clz.video_episode and clz.video_episode[video_episode].name == '':
                clz.video_episode[video_episode].name = video_episode_name
            elif video_episode in clz.video_episode and clz.video_episode[video_episode].name != video_episode_name:
                logger.warning(
                    f'Detected conflict episode name `{video_episode_name}` expected `{clz.video_episode[video_episode].name}` at {__file__} line {sys._getframe().f_lineno}\n')
        if video_episode not in clz.video_episode:
            clz.video_episode[video_episode] = clz.episode(
                video_episode, video_episode_name, video_extra)
            _set_eps_lang(_filename)
        else:
            _set_eps_lang(_filename)

    def _get_new_filename():
        name = clz.video_name if args.name is None else args.name
        _filename = clz.new_style.replace('@VIDEO_NAME@', name).replace('@VIDEO_SEASON@', 'S' + clz.video_season).replace(
            '@VIDEO_EPISODE@', 'E' + clz.video_episode[video_episode].number).replace(
                '@VIDEO_EPISODE_NAME@', clz.video_episode[video_episode].name).replace(
                    '@VIDEO_EXTRA@', clz.video_episode[video_episode].extra)
        if clz.video_episode[video_episode].name == '':
            _filename = clz.new_style.replace('@VIDEO_NAME@', name).replace('@VIDEO_SEASON@', 'S' + clz.video_season).replace(
                '@VIDEO_EPISODE@', 'E' + clz.video_episode[video_episode].number).replace(
                    '.@VIDEO_EPISODE_NAME@', '').replace(
                        '@VIDEO_EXTRA@', clz.video_episode[video_episode].extra)
        return _filename

    video_files: path = find_video_files(video_dir, recursive=False)
    for file in video_files:
        _, _, video_episode, _, _ = _guess_media_filename_fields(
            file)
        _filename = _get_new_filename()
        filename = f"{_filename.strip('.')}{file.suffix}"
        if file.name.lower() != filename.lower():
            print(f"{file.name} --> {filename}")
            file.rename(path.joinpath(file.parent, f"{filename}"))

    subs_files: path = find_subtitle_files(subs_dir, recursive=False)
    for file in subs_files:
        _, _, video_episode, _, _ = _guess_media_filename_fields(
            file)
        _lang = guess_lang_from_subtitle(file)
        _filename = _get_new_filename()
        filename = f"{_filename.strip('.')}.{_lang}{file.suffix}"
        if file.name.lower() != filename.lower():
            print(f"{file.name} --> {filename}")
            file.rename(path.joinpath(file.parent, f"{filename}"))


if __name__ == "__main__":
    video_dir: path = None
    subs_dir: path = None
    if video_dir is None:
        video_dir = path('videos')
    if subs_dir is None:
        subs_dir = path('subs')
    if not video_dir.exists():
        video_dir = path.cwd()
    if not subs_dir.exists():
        subs_dir = path.cwd()

    run(video_dir, subs_dir)
