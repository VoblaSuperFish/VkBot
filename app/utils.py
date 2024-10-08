"""Модуль, в котором содержатся основные функции приложения.
Отправка сообщений, обращение к API.
"""

import requests
import datetime

import wikipedia

from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from text import Text
from config import BaseConnectSettingsAPI
from logs.baselog import logs, logs_except

connect_setting = BaseConnectSettingsAPI()

text = Text()

wikipedia.set_lang('ru')


class SendingMessageUser:
    def __init__(self, authorise:VkApi):
        self.authorise = authorise

    def write_message(self, sender_id, message):
        """Функция отправки сообщений"""
        self.authorise.method(
            'messages.send', 
            {'user_id' : sender_id, 'message' : message, 'random_id' : get_random_id()}
            )

    def send_sticker(self, sender_id, sticker_number):
        """Функция для отправления стикера пользователю по айди стикера"""
        try:
            self.authorise.method('messages.send',
                        {'user_id' : sender_id,
                        'sticker_id' : sticker_number, 
                        'random_id' : get_random_id()})
            return True
        except Exception as Error:
            logs_except.error('Пользователю не отправился стикер: %s' % (Error))
            return False

    def write_message_add_keyboard(self, 
            sender_id:int, 
            message:str, 
            keyboard_obj:VkKeyboard,
        ):
        """Функция для отправки сообщения + добавления клавиатуры"""
        self.authorise.method(
        'messages.send', {
            'user_id' : sender_id, 
            'message' : message, 
            'random_id' : get_random_id(), 
            'keyboard' : keyboard_obj.get_keyboard()}
        )



def get_info_from_wiki(search_text):
    """Функци получения информации из Wiki по заданному слову"""
    try:
        #Получение страницы в википедии по запросу
        full_content = wikipedia.page(search_text)
        response = f"{full_content.content[:300]}...\nСсылка на статью: {full_content.url}"
        return {'status' : 200, 'content' : response}
    except Exception as error:
        search_list = wikipedia.search(search_text, results=5)
        if search_list:
            #Возвращаем строку возможныx значений, которые имел ввиду пользователь
            return {'status' : 301, 'content' : ("По вашему запросу было найдено несколько "
            "возможных значений, уточните ваш запрос: ") + ", ".join(search_list)}
        return {'status' : 404, 'content' : 'По вашему запросу нет совпадений.'}


def smile_for_weather(weather_street):
    """В зависимости от уличной погоды функция выбирает смайлик"""
    smile = "Смайлика нет :("
    if weather_street in text.code_smile:
        smile = text.code_smile[weather_street]
    return smile

def get_full_response_text(json_response):
    """Преобразование ответа от API погоды из json в текст"""
    time_sunrise = datetime.datetime.fromtimestamp(json_response['sys']['sunrise'])
    time_sunset = datetime.datetime.fromtimestamp(json_response['sys']['sunset'])
    time_day = time_sunset - time_sunrise
    itog_response = f"""
    Полученная информация:
Город: {json_response['name']}
Температура: {json_response['main']['temp']} °C
Влажность: {json_response['main']['humidity']} %
Давление: {json_response['main']['pressure']} мм рт. ст.
Скорость ветра: {json_response['wind']['speed']} м/с
Время восхода солнца: {time_sunrise.time()}
Время заказа солнца: {time_sunset.time()}
Продолжительность дня: {time_day}
Погода на улице: {smile_for_weather(json_response['weather'][0]['main'])}
    """
    return itog_response

def info_from_api_weather(search_text):
    """Функция получения информации о погоде из API"""
    try:
        city = search_text
        url = (f'http://api.openweathermap.org/data/2.5/weather?q={city}'
        f'&lang=ru&units=metric&appid={connect_setting.TOKEN_WEATHER}')
        response = requests.get(url, headers=connect_setting.headers, timeout=5)
        if response.status_code in [200,201]:
            text_response = get_full_response_text(response.json())
            return {'status' : 200, 'content' : text_response}
        elif response.status_code == 404:
            return {'status' : 404, 'content' : text.no_found_city}
        else:
            return {"status" : 500, 'content' : text.exceptionn_500}
    except Exception as Error:
        logs_except.error('Ошибка %s при запросе "%s" погодных условий' % (Error, search_text))
        return {"status" : 500, 'content' : text.exceptionn_500}

def info_from_api_numbers(search_text: str):
    """Функция получения факта об числе из API"""
    try:
        number = search_text
        url = f"http://numbersapi.com/{number}"
        response = requests.get(url, headers=connect_setting.headers)
        if response.status_code in [200,201]:
            content_response = response.text
            return {'status' : 200, 'content' : content_response}
        elif response.status_code == 404:
            return {'status' : 404, 'content' : text.user_write_no_number}
    except Exception as Error:
        logs_except.error('Ошибка %s при запросе "%s" факта об числе' % (Error, search_text))
        return {'status' : 500, 'content' : text.exceptionn_500}


def confirm_response(list_text_notes_user, basing_text:str=None):
    """Функция для создания текста из массива заметок пользователя"""
    count = 1
    confirm_string = """"""
    if basing_text:
        confirm_string += basing_text
    for one_text in list_text_notes_user:
        confirm_string += f'{count}. {one_text}.\n'
        count+=1
    return confirm_string