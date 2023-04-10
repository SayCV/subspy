import time

import dl_translate as dlt
import nltk


class DeepLearningTranslator:
    # model
    #   facebook/m2m100_418M facebook/mbart-large-50-many-to-many-mmt
    #   "mbart50" or "m2m100"
    # device
    #   "auto" "cpu" or "gpu"
    def __init__(self, model="m2m100", device="auto"):
        self.device = device
        self.model = model
        self.mt = dlt.TranslationModel(model_or_path=model, device=device)

    def info(self):
        print(dlt.utils.available_languages('mbart50'))  # All languages that you can use
        print(dlt.utils.available_codes('mbart50'))  # Code corresponding to each language accepted
        print(dlt.utils.get_lang_code_map('mbart50'))  # Dictionary of lang -> code

    def test(self):

        #nltk.download("punkt")
        text = "Mr. Smith went to his favorite cafe. There, he met his friend Dr. Doe."
        sents = nltk.tokenize.sent_tokenize(
            text, "english")  # don't use dlt.lang.ENGLISH

        source=dlt.lang.ENGLISH
        target=dlt.lang.CHINESE
        translated_sents = self.mt.translate(sents, source, target, batch_size=32, verbose=True)
        print(' '.join(translated_sents))

    def translate(self, text_list: list, translator: str, from_language: str, to_language: str) -> str:
        source = from_language
        target = to_language
        if from_language == 'chs':
            source = dlt.lang.CHINESE
        if from_language == 'eng':
            source = dlt.lang.ENGLISH
        if to_language == 'chs':
            target = dlt.lang.CHINESE
        if to_language == 'eng':
            target = dlt.lang.ENGLISH
        result = self.mt.translate(text_list, source, target, batch_size=32, verbose=True)
        return '\n'.join(result)


if __name__ == "__main__":
    trans = DeepLearningTranslator()
    trans.info()
    trans.test()