import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os
import threading
import queue
import time

t1 = time.perf_counter()
que = queue.Queue()


def storage_queue(f):
    def wrapper(*args):
        que.put(f(*args))
    return wrapper


# Define the source and target languages
source_language = 'en'
target_languages = ['ur']
#   "af", # Afrikaans
#   "am", # Amharic
#   "ar", # Arabic
#   "hy", # Armenian
#   "az", # Azerbaijani
#   "eu", # Basque
#   "be", # Belarusian
#   "bn", # Bengali
#   "bs", # Bosnian
#   "bg", # Bulgarian
#   "ca", # Catalan
#   "ceb", # Cebuano
#   "zh-CN", # Chinese (Simplified)
#   "zh-TW", # Chinese (Traditional)
#   "co", # Corsican
#   "hr", # Croatian
#   "cs", # Czech
#   "da", # Danish
#   "nl", # Dutch
#   "en", # English
#   "eo", # Esperanto
#   "et", # Estonian
#   "fi", # Finnish
#   "fr", # French
#   "fy", # Frisian
#   "gl", # Galician
#   "ka", # Georgian
#   "de", # German
#   "el", # Greek
#   "gu", # Gujarati
#   "ht", # Haitian Creole
#   "ha", # Hausa
#   "haw", # Hawaiian
#   "he", # Hebrew
#   "hi", # Hindi
#   "hmn", # Hmong
#   "hu", # Hungarian
#   "is", # Icelandic
#   "ig", # Igbo
#   "id", # Indonesian
#   "ga", # Irish
#   "it", # Italian
#   "ja", # Japanese
#   "jv", # Javanese
#   "kn", # Kannada
#   "kk", # Kazakh
#   "km", # Khmer
#   "rw", # Kinyarwanda
#   "ko", # Korean
#   "ku", # Kurdish
#   "ky", # Kyrgyz
#   "lo", # Lao
#   "la", # Latin
#   "lv", # Latvian
#   "lt", # Lithuanian
#   "lb", # Luxembourgish
#   "mk", # Macedonian
#   "mg", # Malagasy
#   "ms", # Malay
#   "ml", # Malayalam
#   "mt", # Maltese
#   "mi", # Maori
#   "mr", # Marathi
#   "mn", # Mongolian
#   "my", # Myanmar (Burmese)
#   "ne", # Nepali
#   "no", # Norwegian
#   "ny", # Nyanja (Chichewa)
#   "or", # Odia (Oriya)
#   "ps", # Pashto
#   "fa", # Persian
#   "pl", # Polish
#   "pt", # Portuguese
#   "pa", # Punjabi
#   "ro", # Romanian
#   "ru", # Russian
#   "sm", # Samoan
#   "gd", # Scots Gaelic
#   "sr", # Serbian
#   "st", # Sesotho
#   "sn", # Shona
#   "sd", # Sindhi
#   "si", # Sinhala (Sinhalese)
#   "sk", # Slovak
#   "sl", # Slovenian
#   "so", # Somali
#   "es", # Spanish
#   "su", # Sundanese
#   "sw", # Swahili
#   "sv", # Swedish
#   "tg", # Tajik
#    "ta", # Tamil
#    "tt", # Tatar
#    "te", # Telugu
#    "th", # Thai
#    "ti", # Tigrinya
#    "to", # Tonga
#    "lua", # Tshiluba
#    "tum", # Tumbuka
#    "tr", # Turkish
#    "tk", # Turkmen
#    "tw", # Twi
#    "ug", # Uighur
#    "uk", # Ukrainian
#    "ur", # Urdu
#    "uz", # Uzbek
#    "vi", # Vietnamese
#    "cy", # Welsh
#    "wo", # Wolof
#    "xh", # Xhosa
#    "yi", # Yiddish
#    "yo", # Yoruba
#    "zu" # Zulu
#   ]  # Example list of target languages

# Parse the original strings.xml file
tree = ET.parse('src/strings.xml')
root = tree.getroot()

parent_directory = "src"
# Loop through the strings and translate them for each target language
for target_language in target_languages:
    newDirectory = f'values-{target_language}'
    # if os.path.isdir(os.path.join(parent_directory, newDirectory)):
    os.mkdir(os.path.join(parent_directory, newDirectory))


# create a lock object
lock = threading.Lock()


def translate(sourceLang, targetLang, stringInput, i):
    string_id = stringInput.attrib['name']
    string_value = stringInput.text
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl={sourceLang}&tl={targetLang}&dt=t&q={string_value}'
    response = requests.get(url)
    data = response.json()
    translatedText = data[0][0][0]
    print(translatedText)

    return {
        'row_number': i,
        'query': stringInput,
        'translation': translatedText
    }
    # acquire the lock before writing to the file
    # with lock:
    #     with open(target_file, 'a') as f:
    #         f.write(f'\t<string name="{string_id}">{translatedText}</string>\n')
    
      

  # create the queue to store the results


# Loop through the strings and translate them for each target language
for target_language in target_languages:

    translationThreads = []
    
    # Create a new strings.xml file for the target language
    target_file = f'{parent_directory}/values-{target_language}/strings.xml'
    with open(target_file, 'w') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n')

    for string in root.iter('string'):

        thread = threading.Thread(target=translate, args=(source_language, target_language, string))
        thread.start()
        translationThreads.append(thread)


    # wait for all threads to finish
    for thread in translationThreads:
        thread.join()



    # Close the resources tag in the target file
    with open(target_file, 'a') as f:
        f.write('</resources>')

print(time.perf_counter() - t1)
