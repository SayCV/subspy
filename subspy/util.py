import chardet

def string_split(string: str, separators: str):
    # 将传进来的列表放入统一的数组中
    result_split = [string]
    # 使用for循环每次处理一种分割符
    for sep in separators:
        # 使用map函数迭代result_split字符串数组
        string_temp = []    # 用于暂时存储分割中间列表变量
        list(
              map(
                 lambda sub_string: string_temp.extend(sub_string.split(sep)),
                 result_split
                 )
             )
        # 经过上面的指令，中间变量string_temp就被分割后的内容填充了，
        # 将分割后的内容赋值给result_split，并作为函数返回值即可
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
    if fn_fields.count >=3:
        lang = fn_fields[fn_fields.count - 2]
    return lang
