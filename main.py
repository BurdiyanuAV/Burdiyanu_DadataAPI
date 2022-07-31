from dadata import Dadata
import sqlite3
import httpx


def get_settings():
    conn = sqlite3.connect('user_settings.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM settings;")
    settings = dict(cur.fetchall())
    conn.commit()
    cur.close()
    return settings


def set_settings(settings):
    conn = sqlite3.connect('user_settings.db')
    cur = conn.cursor()
    for key, value in settings.items():
        cur.execute(f"UPDATE settings SET value = '{value}' WHERE name = '{key}'")
    conn.commit()
    cur.close()
    return


def change_settings(settings):
    handled = False
    while not handled:
        print('\n\n\n       ""Изменение пользовательских настроек""     \n')
        print(f"        Пользовательские настройки\n"
              f"API-ключ:               {settings['API_key']}\n"
              f"Секретный ключ:         {settings['secret']}\n"
              f"Язык:                   {settings['language']}\n"
              f"Количество вариантов:   {settings['variants']}\n")
        print('     --- Что вы хотите изменить?  ---     \n'
              '     (введите число и нажмите Enter)\n'
              '1) API-ключ \n'
              '2) Секретный ключ \n'
              '3) Язык \n'
              '4) Количество вариантов\n'
              '5) Ничего (вернуться в основное меню)\n')

        # Выбор варианта
        variant_chosen = False
        while not variant_chosen:
            x = input('Выбрать ')
            variant_chosen = True
            # Изменение API-ключа
            if x == '1':
                print(f"\n\nСтарый API ключ:    {settings['API_key']}")
                new_api_key = input('Новый API ключ:     ')
                settings['API_key'] = new_api_key
                set_settings(settings)
                print('\n\n\n       --- API ключ успешно изменен ---\n')

            elif x == '2':
                print(f"\n\nСтарый секретный ключ:    {settings['secret']}")
                new_secret = input('Новый секретный ключ:     ')
                settings['secret'] = new_secret
                set_settings(settings)
                print('\n\n\n       --- Секретный ключ успешно изменен ---\n')

            # Изменение языка
            elif x == '3':
                print('\n\n     --- Какой язык вы хотите установить? ---\n'
                      '         (введите число и нажмите Enter)')
                print('1) Русский (ru)\n'
                      '2) Английский (en)\n')
                while True:
                    i = input('Выбрать ')

                    if i == '1':
                        settings['language'] = 'ru'
                        set_settings(settings)
                        break
                    elif i == '2':
                        settings['language'] = 'en'
                        set_settings(settings)
                        break
                    else:
                        print('Неправильный ввод. Пожалуйста, введите число от 1 до 2 и нажмите Enter.')

            # Изменение кол-ва вариантов
            elif x == '4':
                print('\n\n         --- Сколько вариантов должно выводиться в качестве подсказок? ---\n'
                      '                    (введите число от 1 до 20 и нажмите Enter)\n')
                print(f"Установленное значение:      {settings['variants']}")

                while True:
                    try:
                        i = input('Новое значение:              ')
                        if 1 <= int(i) <= 20:
                            settings['variants'] = i
                            set_settings(settings)
                            break
                        else:
                            print('Неправильный ввод. Пожалуйста, введите число от 1 до 20 и нажмите Enter.')
                    except ValueError:
                        print('Неправильный ввод. Введите целое число.')

            # Возврат в основное меню (выход из функции)
            elif x == '5':
                handled = True
            else:
                print('Неправильный ввод. Пожалуйста, введите число от 1 до 4 и нажмите Enter.')
                variant_chosen = False


def show_description():
    print('\n\n\n                       ""Описание программы""  \n')
    print('Данная программа позволяет получить координаты по вводимому адресу.\n'
          'Получение координат осуществляется при помощи API сервиса dadata.ru.\n'
          'Адрес вводится пользователем в свободной форме. Для уточнения адреса\n'
          'используется сервис подсказок адресов dadata.\n')
    print('В программе присутствуют следующие пользовательские настройки:\n'
          '1. API-ключ - ключ, необходимый для использования сервисов dadata. Для\n'
          'получения API ключа Вам необходимо зарегистрироваться в сервисе, после\n'
          'чего необходимые данные будут доступны в Вашем личном кабинете по ссылке:\n'
          'https://dadata.ru/profile/#info\n'
          'Без рабочего API-ключа использование программы невозможно!\n'
          '2. Секретный ключ - еще один ключ, который доступен в личном кабинете\n'
          'https://dadata.ru/profile/#info. Данный ключ необходим для некоторых сервисов\n'
          'dadata.\n'
          '3. Язык - язык, на котором будут представляться подсказки. Английский en\n'
          'или русский ru (по умолчанию).\n'
          '4. Количество вариантов - количество адресов, которые представляются в\n'
          'качестве подсказок при выборе точного адреса. Dadata позволяет выбирать\n'
          'значения от 1 до 20.\n')
    input('     --- Нажмите Enter, чтобы вернуться в основное меню ---')


def coords(settings):
    print('\n\n\n     --- Определение координат ---   \n')
    # variants = []
    # address = ""
    handled = False
    while not handled:
        try:
            address = input('Введите адрес в свободной форме:   ')
            with Dadata(settings['API_key'], settings['secret']) as dadata:
                variants = dadata.suggest(name='address', query=address, count=settings['variants'],
                                          language=settings['language'])

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 400:
                print('\nНекорректный запрос. Невалидный XML или JSON.')
            elif exc.response.status_code == 401:
                print('\nОшибка. Отсутсутствует API-ключ или секретный ключ.\n'
                      'Пожалуйста, установите действительные ключи в пользовательских настройках.')
            elif exc.response.status_code == 403:
                print('\nОшибка. В запросе указан несуществующий API-ключ.\n'
                      'Или не подтверждена почта. Или исчерпан дневной лимит по количеству запросов\n'
                      'Пожалуйста, установите действительный API-ключ в пользовательских настройках.')
            elif exc.response.status_code == 405:
                print('\nОшибка. Запрос сделан с методом, отличным от POST.')
            elif exc.response.status_code == 413:
                print('\nОшибка. Слишком большая длина запроса или слишком много условий.')
            elif exc.response.status_code == 429:
                print('\nОшибка сервиса. Слишком много запросов в секунду или новых соединений в минуту.')
            else:
                print('\nЗапрос не обработан. Произошла внутренняя ошибка сервиса.')

            input('\n     --- Нажмите Enter, чтобы вернуться в основное меню ---')
            return

        except (httpx.LocalProtocolError, UnicodeEncodeError):
            print('\nОшибка. Пожалуйста, проверьте правильность ввода ключей.')
            input('\n     --- Нажмите Enter, чтобы вернуться в основное меню ---')
            return

        print('\nВозможно вы имели ввиду один из этих адресов:')
        for i in range(len(variants)):
            print(f"{i + 1}) {variants[i]['value']}")
        print('\n         --- Выберите нужный адрес или одно из действий ---  \n'
              'а) Уточнить адрес (ввести адрес заново)\n'
              'б) Вернуться в основное меню\n')

        while True:
            x = input('Выбрать (определение координат) ')
            # сначала проверяем буквы, затем цифры (чтобы ловить ошибку)
            try:
                if x == 'а':        # уточнить адрес
                    break
                elif x == 'б':      # выход
                    handled = True
                    break
                # Основной функционал
                elif 0 < int(x) <= len(variants):
                    address = variants[int(x) - 1]['value']
                    print('\n\n\n------------------------------------------------------------')
                    print(f"\n- Вы выбрали: {address} -")
                    with Dadata(settings['API_key'], settings['secret']) as dadata:
                        result = dadata.suggest(name="address", query=address, count=1)
                        latitude = result[0]['data']['geo_lat']     # широта
                        longitude = result[0]['data']['geo_lon']     # долгота
                        print(f"\nШирота:       {latitude}"
                              f"\nДолгота:      {longitude}\n")
                        print('------------------------------------------------------------\n\n')
                else:
                    print(f'Неправильный ввод. Введите число от 1 до {len(variants)} или буквы русского алфавита а, б.')
            except ValueError:
                print(f'Неправильный ввод. Введите число от 1 до {len(variants)} или буквы русского алфавита а, б.')


def main():
    working = True
    # Основной цикл
    while working:
        settings = get_settings()
        print('\n\n\n     ""Dadata. Определение координат по адресу""\n')
        print(f"            Пользовательские настройки\n"
              f"API-ключ:               {settings['API_key']}\n"
              f"Секретный ключ:         {settings['secret']}\n"
              f"Язык:                   {settings['language']}\n"
              f"Количество вариантов:   {settings['variants']}\n")

        print('     --- Выберите действие ---     \n'
              '  (введите число и нажмите Enter)\n'
              '1) Определение координаты по адресу\n'
              '2) Изменение пользовательских настроек\n'
              '3) Описание программы\n'
              '4) Выход\n')

        while True:
            x = input('Выбрать ')
            if x == '1':
                coords(settings)
                break
            elif x == '2':
                change_settings(settings)
                break
            elif x == '3':
                show_description()
                break
            elif x == '4':
                working = False
                break
            else:
                print('\nНеправильный ввод. Пожалуйста, введите число от 1 до 4 и нажмите Enter.\n')


if __name__ == '__main__':
    main()
