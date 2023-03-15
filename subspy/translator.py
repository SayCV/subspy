from typing import Iterator, List
import translators as ts
import time

class SubspyTranslator:
    def __init__(self, engine='bing'):
        self.engine: str = engine
        self.limit_of_length: int = 5000
        if self.engine == 'bing':
            self.limit_of_length = 900
        # ts.preaccelerate()  # Optional. Caching sessions in advance, which can help improve access speed.

    def get_char_limit(self) -> int:
        return self.limit_of_length

    def _translate(self, query_text: str, translator: str, from_language: str, to_language: str) -> str:
        result = ts.translate_text(query_text, translator, from_language, to_language)
        return result

    def translate(self, text_list: list, translator: str, from_language: str, to_language: str) -> str:
        result = self.translate_lines(text_list, translator, from_language, to_language)
        return result

    def translate_lines(self, text_list: list, translator: str, from_language: str, to_language: str) -> str:
        translated = ''
        last_idx = 0
        total_length = 0
        for i in range(len(text_list)):
            total_length += len(text_list[i])
            if total_length > self.limit_of_length:
                translated += self._translate(
                    '\n'.join(text_list[last_idx:i]), translator, from_language, to_language)
                translated += '\n'
                time.sleep(1)
                last_idx = i
                total_length = 0
        translated += self._translate(
            '\n'.join(text_list[last_idx:]), translator, from_language, to_language)
        translated = translated.replace('\n\n', '\n')
        translated = translated.replace('……', '…')
        translated = translated.replace('——', '-')
        translated = translated.replace('♬', '♪')
        translated = translated.replace('< / i >', '</i>')
        translated = translated.replace('<我>', '<i>')
        translated = translated.replace('</我>', '</i>')
        translated = translated.replace('\u6027\u4ea4', 'TMD')
        translated = translated.strip('\n')
        return translated

