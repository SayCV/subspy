"""
"""

import logging
import mimetypes
import re
import sys
from pathlib import Path as path
from pprint import pprint

from subspy.helpers import count_characters_chinese_english
from subspy.util import guess_lang

logger = logging.getLogger(__name__)

filename_delims = '.- '

default_filename_pattern = r"(?P<p_video_name>.*)[\.\- ]?[sS](?P<p_video_season>\d\d)[\.\- ]?[eE](?P<p_video_episode>\d\d)[\.\- ]?(?P<p_video_episode_name>[,\^:^!\w.\-\'\(\)]*)[\.\- ]+\d{3,5}p.*"

new_filename_style = r"@VIDEO_NAME@.@VIDEO_SEASON@@VIDEO_EPISODE@.@VIDEO_EPISODE_NAME@.@VIDEO_SUFFIX@"

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
                fullpath = name #dirpath / name
                if is_video_file(fullpath):
                    results.append(fullpath)
    else:
        for entry in directory.iterdir():
            fullpath = entry #directory / entry
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
                fullpath = name #dirpath / name
                if is_subtitle_file(fullpath):
                    results.append(fullpath)
    else:
        for entry in directory.iterdir():
            fullpath = entry #directory / entry
            if fullpath.is_file() and is_subtitle_file(fullpath):
                results.append(fullpath)

    return sorted(results)

def _guess_video_filename_fields(filename: path, pattern = None):
    logger.debug(f'Processing: {filename.name}')
    pattern = default_filename_pattern if pattern is None else pattern
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
        video_episode_name = _fields[u'p_video_episode_name']
    else:
        video_episode_name = None

    logger.debug(f'Succeeded to guess fields: {video_name},{video_season},{video_episode},{video_episode_name}')
    return (video_name, video_season, video_episode, video_episode_name)

def guess_fields_from_video(directory: path, recursive=False):
    results = []
    video_files = find_video_files(directory, recursive=False)

    for filename in video_files:
        #_, video_season, video_episode, video_episode_name = _guess_video_filename_fields(filename)
        results.append(_guess_video_filename_fields(filename))
    return results

def guess_fields_from_subtitle(directory: path, recursive=False):
    results = []
    subs_files = find_subtitle_files(directory, recursive=False)

    for filename in subs_files:
        #_, video_season, video_episode, video_episode_name = _guess_video_filename_fields(filename)
        results.append(_guess_video_filename_fields(filename))
    return results

def guess_lang_from_subtitle(directory: path, recursive=False):
    results = []
    subs_files = find_subtitle_files(directory, recursive=False)

    for filename in subs_files:
        in_lang = guess_lang(filename.name)
        if in_lang is None:
            en_count, zh_cn_count, zh_tw_count = count_characters_chinese_english(filename)
            lang = []
            if en_count > 500:
                lang.append('eng')
            if zh_cn_count > 500:
                lang.append('chs')
            if zh_tw_count > 100:
                lang.append('cht')
            results.append('+'.join(lang))
        else:
            results.append(in_lang)
    return results

def run(video_dir: path, subs_dir: path, recursive=False):
    if video_dir is None:
        video_dir = path('videos')
    if subs_dir is None:
        subs_dir = path('subs')
    if not video_dir.exists():
        video_dir = path.cwd()
    if not subs_dir.exists():
        subs_dir = path.cwd()

    fields_from_video = guess_fields_from_video(video_dir)
    fields_from_subtitle = guess_fields_from_subtitle(subs_dir)
    pprint(fields_from_video)
    print('\r\n\r\n')
    pprint(fields_from_subtitle)
    print('\r\n\r\n')
    lang_from_subtitle = guess_lang_from_subtitle(subs_dir)
    pprint(lang_from_subtitle)

if __name__ == "__main__":
    video_dir = path('')
    subs_dir = path('')
    run(video_dir, subs_dir)
