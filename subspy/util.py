import chardet


def get_encoding(filename):
    with open(filename, "rb") as f:
        res = chardet.detect(f.read())
    return res['encoding']
