#!/usr/bin/env python3

"""
A Watson-Translation Utility/Interface for the API v3.
Copyright (C) 2019 Peter Maar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

"""


from watson_developer_cloud import LanguageTranslatorV3
from watson_developer_cloud.watson_service import WatsonApiException
import re
import os
import json

# 0 Dallas, 1 Washington DC, 2 Frankfurt, 3 Sydney, 4 Tokyo, 5 London
LOCATION_NUMBER = 1

url_locations = ["", "-wdc", "-fra", "-syd", "-tok", "-lon"]
url_location = url_locations[LOCATION_NUMBER]

# Detections contains {phrase: lang}
# Translations contains {input_lang: {output_lang: {input_phrase: output_phrase}}}
saved_translations = {'detections': {}, 'translations': {}}
saved_translations_path = os.path.normpath('saved_translations.json')


def load_translations():
    global saved_translations

    if os.path.isfile(saved_translations_path):
        saved_translations_file = open(saved_translations_path)

        translation_file_contents = saved_translations_file.read()  # Read the contents

        if len(str.rstrip(translation_file_contents)) != 0:
            saved_translations = json.loads(translation_file_contents)  # Read and decode the JSON from the file
            print(saved_translations)

        saved_translations_file.close()


def save_translations():
    print("Saving...")
    saved_translations_file = open(saved_translations_path, 'w')
    saved_translations_file.write(json.dumps(saved_translations))  # Write the translations
    saved_translations_file.close()
    print("Saved!")


class WatsonTranslator:
    def __init__(self, version, api_key):
        self.version = version
        self.api_key = api_key
        
        self.language_translator = LanguageTranslatorV3(
            version='2018-05-01',
            iam_apikey=self.api_key,
            url='https://gateway' + url_location + '.watsonplatform.net/language-translator/api')

        if saved_translations == {'detections': {}, 'translations': {}}:
            load_translations()

    def auto_translate(self, input_text, output_language='en', pick_language=0):
        """

        :param input_text:
        :param output_language:
        :param pick_language:
        :return: The translated text, the detected language.
        """
        if pick_language > 5:  # If we take too many tries, give up and just use the original text
            print("Too many tries")
            return input_text, output_language

        input_language = self.detect_language(input_text, pick_language=pick_language)

        try:
            output_text = self.translate_text(input_text, input_language, output_language)
        except WatsonApiException as e:
            if e.message == "Model not found.":
                return self.auto_translate(input_text, pick_language=pick_language + 1)
            else:
                raise e

        return output_text, input_language

    def detect_language(self, input_text, pick_language=0):
        print("Detecting", input_text)

        if input_text in saved_translations['detections']:
            print("Using previously detected")
            return saved_translations['detections'][input_text]

        input_language = self.language_translator.identify(input_text).get_result()
        confidence = input_language["languages"][pick_language]['confidence']
        input_language = input_language["languages"][pick_language]["language"]

        print("Result:", input_language, confidence)

        if confidence > 0.3:
            saved_translations['detections'][input_text] = input_language
            return input_language
        else:
            saved_translations['detections'][input_text] = 'en'
            return 'en'

    def translate_text(self, input_text, input_language, output_language, emoji_names=[]):
        if input_language == output_language:
            return input_text

        print("Translating", input_text, input_language, output_language)

        if input_language in saved_translations['translations']:
            if output_language in saved_translations['translations'][input_language]:
                if input_text in saved_translations['translations'][input_language][output_language]:
                    print("Using saved translation")
                    return saved_translations['translations'][input_language][output_language][input_text]


        input_list = re.split('(:|_|\*|~~)', input_text)

        output_list = self.language_translator.translate(
            text=input_list,
            model_id=input_language + '-' + output_language).get_result()

        print('==============================')
        print(input_list)
        print(output_list['translations'])
        print('==============================')

        output_text = ""

        for i in range(0, len(output_list['translations'])):
            added_char = False
            if input_list[i] == "":
                continue

            for c in [':', '_', '*', '~~']:
                if input_list[i] == c:
                    output_text += c
                    added_char = True
                    break

            if not added_char:
                if input_list[i] in emoji_names and input_list[i + 1] == ":":
                    output_text += input_list[i]
                elif i < len(output_list['translations']) - 2 and ((input_list[i] + input_list[i+1] + input_list[i+2]) in emoji_names):
                        output_text += input_list[i] + input_list[i+1] + input_list[i+2]
                        input_list[i] = ""
                        input_list[i + 1] = ""
                        input_list[i + 2] = ""
                else:
                    output_text += output_list['translations'][i]['translation']

        print("Result:", output_text)

        if input_language not in    saved_translations['translations']:
            saved_translations['translations'][input_language] = {}

        if output_language not in   saved_translations['translations'][input_language]:
            saved_translations['translations'][input_language][output_language] = {}

        if input_text not in        saved_translations['translations'][input_language][output_language]:
            saved_translations['translations'][input_language][output_language][input_text] = output_text

        return output_text


if __name__ == "__main__":
    translator_api_path = os.path.normpath('ID/TRANSLATOR_API_KEY.txt')
    TRANSLATOR_API_KEY = str.rstrip(open(translator_api_path).read())
    wt = WatsonTranslator('2019-05-21', TRANSLATOR_API_KEY)
    print('Test Result:', wt.auto_translate("_Hola, soy Niko! ¿Cómo estás?_ :niko_speak:"))

save_translations()
