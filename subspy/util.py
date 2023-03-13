import chardet


def string_split(string: str, separators: str):
    result_split = [string]
    for sep in separators:
        string_temp = []
        list(
              map(
                 lambda sub_string: string_temp.extend(sub_string.split(sep)),
                 result_split
                 )
             )
        result_split = string_temp

    return result_split

def guess_encoding(filename: str):
    with open(filename, "rb") as f:
        res = chardet.detect(f.read())
    return res['encoding']

def guess_lang(filename: str, delims = None):
    if delims is None:
        delims = '.- '
    fn_fields = string_split(filename, delims)

    lang = None
    count = len(fn_fields)
    if count >=3:
        lang = fn_fields[count - 2]
    return lang
