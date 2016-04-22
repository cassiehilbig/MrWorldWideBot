import translate
from translate import Translator

def translateshit(to_lang, text):
    translator= Translator(to_lang=to_lang)
    return translator.translate(text)