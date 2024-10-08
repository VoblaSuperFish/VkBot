"""Базовый модуль запуска приложения и обработка сообщений пользователя"""

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from text import Text
from config import BaseSettingApp
from keyboards import KeyBoard
from utils import SendingMessageUser
from database.db import create_table,drop_table,get_session #type:ignore
from database.orm import UsersOrm, NotesOrm
from logs.baselog import logs, logs_except
from handlers import (
    handler_wiki, handler_weather, handler_number,
    handler_mailing,handler_writing_notes,
    handler_show_notes,handler_start_deleted_notes,
    handler_deleted_notes
)


keyboard:KeyBoard = KeyBoard()
text = Text()

user_orm = UsersOrm(get_session())
note_orm = NotesOrm(get_session())

setting_app = BaseSettingApp()

authorise = vk_api.VkApi(token=setting_app.TOKEN_BOT)
longpoll = VkLongPoll(authorise)

send_func = SendingMessageUser(authorise)

try:
    create_table()
    logs.warning('База данных была создана')
except Exception as Error:
    logs.error('Ошибка при создании базы данных: %s' % (Error))

logs.warning('Приложение запущено')

try:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            sending_text = event.text
            sender_id = event.user_id
            logs.info('Пользователь с id %s отправил сообщение "%s"' %       
                        (sender_id, sending_text))
            #Остановка программы (только если бот в режиме разработки)
            if sending_text == '/debug_stop':
                if setting_app.PROGRAM_IN_DEBUG:
                    logs.warning('Произошло экстренное выключение приложения')
                    raise Exception

            """Получение пользователя из базы данных и создание его, если такого ещё нет"""
            user_from_orm = user_orm.get_user_from_db(sender_id)
            if not user_from_orm:
                user_orm.create_user_in_db(sender_id)
                user_from_orm = user_orm.get_user_from_db(sender_id)
                logs.info('Пользователь с id %s добавлен в базу' % (sender_id))
            user = user_from_orm['Users']

            """Если пользователь не в ожидании запроса ввода"""
            if not user.in_process:
                try:
                    if sending_text.lower() in ['старт', 'привет', 'hello', '/start']:
                        """Начальное приветствие пользователя"""
                        send_func.send_sticker(sender_id, 21)
                        send_func.write_message_add_keyboard(sender_id, 
                            text.hello_user, 
                            keyboard.keyboard_hello
                            )
                    
                    elif sending_text.lower() in ['/help', 'помощь', 'help']:
                        """Пользователь запросил помощи"""
                        send_func.write_message_add_keyboard(
                            sender_id, text.help_user, keyboard.keyboard_hello
                            )

                    elif sending_text.lower() in ['/wiki', 'вики', 'информация из wiki']:
                        """Пользователь запросил функцию поиска по вики"""
                        send_func.write_message_add_keyboard(
                            sender_id, text.wiki_start, keyboard.keyboard_exit
                            )
                        user_orm.update_status_user_wiki(sender_id, status=True)

                    elif sending_text.lower() in ['/weathers', 'информация о погоде', 
                                                '/weather', 'погода']:
                        """Пользователь запросил функцию поиска информации о погоде"""
                        send_func.write_message_add_keyboard(
                            sender_id, text.weather_start, keyboard.keyboard_exit
                            )
                        user_orm.update_status_user_weather(sender_id, status=True)

                    elif sending_text.lower() in ['/numbers', "получить интереный факт", '/number']:
                        """Если пользователь захотел получить интересный факт о числе"""
                        send_func.write_message_add_keyboard(
                            sender_id, text.number_start, keyboard.keyboard_exit
                            )
                        user_orm.update_status_user_number(sender_id, status=True)

                    elif sending_text.lower() == '/sends':
                        if user.is_superuser:
                            """Если пользователь захотел сделать рассылку + 
                            является супер пользователем
                            """
                            send_func.write_message_add_keyboard(
                                sender_id, text.mailing_start, keyboard.keyboard_mailing
                                )
                            user_orm.update_status_mailing_before(sender_id, status=True)
                        else:
                            send_func.write_message_add_keyboard(sender_id, 
                            'У вас нет прав на использование этой команды.', 
                            keyboard.keyboard_hello
                            )

                    elif sending_text.lower() in ['/notes', 'заметки']:
                        """Если пользователь захотел получить информацию о заметках"""
                        send_func.write_message_add_keyboard(sender_id, 
                            text.notes_start, keyboard.keyboard_notes
                            )

                    elif sending_text.lower() in ['добавить заметку', '/add_notes']:
                        """Если пользователь захотел добавить заметку"""
                        send_func.write_message_add_keyboard(sender_id, 
                                text.notes_start_add, 
                                keyboard.keyboard_stopped_input
                            )
                        user_orm.update_status_add_notes(sender_id, status=True)

                    elif sending_text.lower() in ['получить свои заметки', '/show_notes']:
                        """Если пользователь захотел получить свои заметки"""
                        handler_show_notes(send_func=send_func, sender_id=sender_id, note_orm=note_orm)
                    
                    elif sending_text.lower() in ['удалить заметки', '/delete_notes']:
                        """Если пользователь захотел удалить свои заметки"""
                        handler_start_deleted_notes(
                            send_func=send_func,
                            sender_id=sender_id,
                            note_orm=note_orm,
                            user_orm=user_orm,)
                    
                    elif sending_text.lower() in ['/stop', 'отмена']:
                        """Если пользователь нажал кнопку отмена, но он не находится в режиме ввода
                        """
                        send_func.write_message_add_keyboard(sender_id, 
                            text.no_exit, keyboard.keyboard_hello,
                            )

                    elif sending_text.lower() in ['/stop_input', 'остановить ввод']:
                        """Если пользователь захотел выйти из режима ввода,
                        когда он в нём не находился
                        """
                        send_func.write_message(sender_id, text.no_input_message)

                    else:
                        """Если команда, которую ввел человек не найдена"""
                        send_func.write_message_add_keyboard(sender_id, 
                            text.no_command_search, keyboard.keyboard_no_command
                            )
                except Exception as Error:
                    logs_except.error('Ошибка при выборе функции: %s' % (Error))
                    send_func.write_message(sender_id, text.exceptionn_500)
            #Если пользователь находится в статусе запроса ввода
            else:
                try:
                    if sending_text.lower() in ['/stop', 'отмена']:
                        """Если пользователь нажал кнопку отмена, в любом режиме ввода"""
                        user_orm.update_full_process(sender_id, full_status=False)
                        send_func.write_message_add_keyboard(sender_id, 
                            text.exit_all_process, keyboard.keyboard_hello
                            )

                    elif sending_text.lower() in ['/stop_input', 'остановить ввод']:
                        """Если пользователь остановил ввод на добавление или удаление заметок"""
                        user_orm.update_full_process(sender_id, full_status=False)
                        send_func.write_message_add_keyboard(sender_id, 
                            text.stopped_write_or_delete, keyboard.keyboard_notes
                            )

                    elif user.in_process_wiki:
                        """Если пользователь в запросе ввода Wiki данных"""
                        handler_wiki(
                            send_func=send_func, 
                            sender_id=sender_id, 
                            sending_text=sending_text
                            )

                    elif user.in_process_weather:
                        """Если пользователь в запросе ввода города для получения погоды"""
                        handler_weather(
                            send_func=send_func, 
                            sender_id=sender_id, 
                            sending_text=sending_text
                            )

                    elif user.in_process_number:
                        """Если пользователь в запросе воода цифры для получения факта"""
                        handler_number(send_func=send_func, 
                            sender_id=sender_id, 
                            sending_text=sending_text
                            )

                    elif user.in_process_mailing:
                        """Если пользователь ввел сообщение для рассылки"""
                        list_users_id = user_orm.get_list_vk_id()
                        handler_mailing(
                            send_func=send_func, 
                            sending_text=sending_text, 
                            list_user=list_users_id
                            )
                        logs.warning('Произошла рассылка админом: %s' % (sender_id))
                        user_orm.update_status_mailing_after(user_id=sender_id, status=False)
                        send_func.write_message(sender_id, text.after_mailing)

                    elif user.in_process_create_note:
                        """Если пользователь ввел заметку, которую нужно добавить"""
                        if len(sending_text) <= 150:
                            handler_writing_notes(
                            send_func=send_func, 
                            sender_id=sender_id,
                            sending_text=sending_text, 
                            note_orm=note_orm
                            )
                        else:
                            send_func.write_message(sender_id, text.limit_warning)

                    elif user.in_process_delete_note:
                        """Если пользователь находится в режиме ожидания ввода номеров заметок
                        для их удаления из базы.
                        """
                        handler_deleted_notes(
                        send_func=send_func, 
                        sender_id=sender_id, 
                        sending_text=sending_text,
                        note_orm=note_orm,
                        user_orm=user_orm
                        )
                except Exception as error:
                    logs_except.error('Ошибка при обработке запроса: %s' % (Error))
                    send_func.write_message(sender_id, text.exceptionn_500)


except Exception as Error:
    logs_except.critical('Приложение выключено, ошибка: %s' % (Error))
finally:
    """Удаление таблиц базы данных, если приложение в режиме разработки"""
    logs.info('Приложение выключено')
    if setting_app.PROGRAM_IN_DEBUG:
        logs.warning('База данных была удалена')
        drop_table()

logs.warning('Приложение выключено')