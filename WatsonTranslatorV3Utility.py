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

# 0 Dallas, 1 Washington DC, 2 Frankfurt, 3 Sydney, 4 Tokyo, 5 London
LOCATION_NUMBER = 1

url_locations = ["", "-wdc", "-fra", "-syd", "-tok", "-lon"]
url_location = url_locations[LOCATION_NUMBER]

class WatsonTranslator:
    def __init__(self, version, api_key):
        self.version = version
        self.api_key = api_key
        
        self.language_translator = LanguageTranslatorV3(
            version='2018-05-01',
            iam_apikey=self.api_key,
            url='https://gateway' + url_location + '.watsonplatform.net/language-translator/api')

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

        input_language = self.language_translator.identify(input_text).get_result()
        confidence = input_language["languages"][pick_language]['confidence']
        input_language = input_language["languages"][pick_language]["language"]

        print("Result:", input_language, confidence)

        if confidence > 0.3:
            return input_language
        else:
            return 'en'

    def translate_text(self, input_text, input_language, output_language, emoji_names=[]):
        if input_language == output_language:
            return input_text

        print("Translating", input_text, input_language, output_language)


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

        return output_text

