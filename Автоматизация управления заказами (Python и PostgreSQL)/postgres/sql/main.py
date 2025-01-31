import psycopg2
import pandas as pd
import configparser
from datetime import datetime
import numpy as np
import csv
import os

# Общие настройки и функции
param_dict = {
    "host": "pg3.sweb.ru",
    "database": "tyrsadocto",
    "user": "tyrsadocto",
    "password": "T5p2fga5c8y"
}

# Словарь с названиями месяцев
month_names = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь"
}

def time_to_minutes(time_str):
    """Преобразует строку времени в минуты."""
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 60 + m + s / 60
    except (ValueError, AttributeError):
        # Если время в неправильном формате, возвращаем 0
        return 0

def calculate_bonus(salary, performance_diff):
    """Рассчитывает премию на основе оклада и разницы в производительности."""
    bonus_percentage = 0.0
    if performance_diff > 0.1:
        bonus_percentage = 0.1  # 10% премии за превышение показателей на 10%
    elif performance_diff > 0.07:
        bonus_percentage = 0.07  # 7% премии за превышение показателей на 7%
    elif performance_diff > 0:
        bonus_percentage = 0.05  # 5% премии за небольшое превышение

    return salary * bonus_percentage

def process_data(df):
    """Обрабатывает данные и выводит результаты."""
    try:
        df['time_minutes'] = df['time'].apply(time_to_minutes)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Преобразуем дату, игнорируя ошибки
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year  # Добавляем столбец с годом

        # Удаляем строки с некорректными данными
        df = df.dropna(subset=['date', 'time_minutes'])

        # Рассчет производительности (мест/час)
        df['hourly_rate_places'] = df['place'] / (df['time_minutes'] / 60)

        # Расчет скорости сборки (мин/место)
        df['minutes_per_place'] = df['time_minutes'] / df['place']

        # Расчет среднего времени сборки заказа в минутах
        average_time_per_order = df['time_minutes'].mean()

        # Расчет количества заказов в день
        orders_per_day = df.groupby('date')['id'].count()
        average_orders_per_day = orders_per_day.mean()

        # Группировка по годам и месяцам
        monthly_stats = df.groupby(['year', 'month']).agg(
            total_orders=('id', 'count'),
            total_time=('time_minutes', 'sum'),
            total_places=('place', 'sum')
        ).reset_index()

        # Находим последний месяц и год в данных
        last_month_stats = monthly_stats.iloc[-1]
        last_year = last_month_stats['year']
        last_month = last_month_stats['month']

        # Прогноз на следующий месяц
        def predict_next_month_kpi(last_month_stats, growth_rate, time_reduction_rate, productivity_growth_rate):
            predicted_stats = last_month_stats.copy()
            predicted_stats['total_orders'] = (last_month_stats['total_orders'] * (1 + growth_rate)).round()
            predicted_stats['total_time'] = (last_month_stats['total_time'] * (1 - time_reduction_rate)).round()
            predicted_stats['total_places'] = (last_month_stats['total_places'] * (1 + growth_rate)).round()
            return predicted_stats

        # Задаем процент роста и уменьшения времени
        growth_rate = 0.05  # 5% рост
        time_reduction_rate = 0.03  # 3% уменьшение времени
        productivity_growth_rate = 0.02  # 2% рост производительности

        # Прогнозируем на следующий месяц
        if last_month == 12:
            next_year = last_year + 1
            next_month = 1
        else:
            next_year = last_year
            next_month = last_month + 1

        predicted_stats = predict_next_month_kpi(last_month_stats, growth_rate, time_reduction_rate, productivity_growth_rate)

        # Сравнение прошлого и текущего месяца
        if last_month == 1:
            previous_year = last_year - 1
            previous_month = 12
        else:
            previous_year = last_year
            previous_month = last_month - 1

        # Ищем данные за предыдущий месяц
        previous_month_stats = monthly_stats[
            (monthly_stats['year'] == previous_year) & (monthly_stats['month'] == previous_month)
        ]

        if not previous_month_stats.empty:
            previous_month_stats = previous_month_stats.iloc[0]

            # Сравнение показателей
            orders_diff = (last_month_stats['total_orders'] - previous_month_stats['total_orders']) / previous_month_stats['total_orders']
            time_diff = (last_month_stats['total_time'] - previous_month_stats['total_time']) / previous_month_stats['total_time']
            places_diff = (last_month_stats['total_places'] - previous_month_stats['total_places']) / previous_month_stats['total_places']

            # Расчет премии
            salary = 80850  # Пример оклада
            performance_diff = (orders_diff + places_diff - time_diff) / 3  # Средняя разница в показателях
            bonus = calculate_bonus(salary, performance_diff)

            result_text = "Сравнение KPI прошлого и текущего месяца:\n"
            result_text += "---------------------------------------\n"
            result_text += f"Изменение количества заказов: {orders_diff:.2%}\n"
            result_text += f"Изменение времени сборки: {time_diff:.2%}\n"
            result_text += f"Изменение количества мест: {places_diff:.2%}\n"
            result_text += f"Рассчитанная премия: {bonus:.2f} руб.\n"
            result_text += "---------------------------------------\n"
        else:
            result_text = "Недостаточно данных для сравнения с прошлым месяцем.\n"
            result_text += "---------------------------------------\n"

        result_text += "Результаты KPI:\n"
        result_text += "---------------------------------------\n"
        result_text += f"Среднее время сборки заказа (мин): {average_time_per_order:.2f}\n"
        result_text += "---------------------------------------\n"

        result_text += "\nСводная статистика по KPI:\n"
        result_text += "---------------------------------------\n"
        result_text += f"Средняя производительность сборки (мест/час): {df['hourly_rate_places'].mean():.2f}\n"
        result_text += f"Средняя скорость сборки (мин/место): {df['minutes_per_place'].mean():.2f}\n"
        result_text += f"Среднее количество заказов в день: {average_orders_per_day:.2f}\n"
        result_text += "---------------------------------------\n"

        result_text += "\nСтатистика по месяцам:\n"
        result_text += "---------------------------------------\n"
        for _, row in monthly_stats.iterrows():
            total_time_hours = row['total_time'] / 60
            month_name = month_names.get(row['month'], "Неизвестный месяц")  # Получаем название месяца
            result_text += f"Месяц: {month_name} {row['year']}\n"
            result_text += f"  Общее количество заказов: {row['total_orders']}\n"
            result_text += f"  Общее время сборки (часы): {total_time_hours:.2f}\n"
            result_text += f"  Общее количество мест: {row['total_places']}\n"
            result_text += "---------------------------------------\n"

        # Расчет прогнозируемой сводной статистики
        predicted_total_places = predicted_stats['total_places']
        predicted_total_time = predicted_stats['total_time']

        # Используем среднюю производительность из исходных данных как базовую
        base_average_hourly_rate_places = df['hourly_rate_places'].mean()
        # Увеличиваем базовую производительность на процент роста производительности
        predicted_average_hourly_rate_places = base_average_hourly_rate_places * (1 + productivity_growth_rate)

        predicted_average_time_per_place = predicted_total_time / predicted_total_places

        result_text += "\nПрогноз KPI на следующий месяц (при росте на {0:.0%} по заказам и местам, уменьшении времени на {1:.0%} и росте производительности на {2:.0%}):\n".format(growth_rate, time_reduction_rate, productivity_growth_rate)
        result_text += "---------------------------------------\n"
        next_month_name = month_names.get(next_month, "Неизвестный месяц")  # Название следующего месяца
        result_text += f"Месяц: {next_month_name} {next_year}\n"
        result_text += f"  Прогнозируемое количество заказов: {predicted_stats['total_orders']}\n"
        result_text += f"  Прогнозируемое время сборки (часы): {predicted_total_time / 60:.2f}\n"
        result_text += f"  Прогнозируемое количество мест: {predicted_stats['total_places']}\n"
        result_text += "---------------------------------------\n"

        result_text += "\nПрогнозируемая сводная статистика:\n"
        result_text += "---------------------------------------\n"
        result_text += f"Прогнозируемая средняя производительность сборки (мест/час): {predicted_average_hourly_rate_places:.2f}\n"
        result_text += f"Прогнозируемое среднее время сборки (мин/место): {predicted_average_time_per_place:.2f}\n"
        result_text += "---------------------------------------\n"

        # Выводим результат в консоль
        print(result_text)
        
        # Сохраняем результаты в CSV
        save_to_csv(result_text)

    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")

def save_to_csv(result_text):
    """Сохраняет результаты в CSV файл."""
    try:
        # Преобразуем текстовые данные в DataFrame
        lines = result_text.split("\n")
        data = []
        for line in lines:
            if line.strip() and "---------------------------------------" not in line:
                data.append([line.strip()])

        df = pd.DataFrame(data, columns=["Результаты KPI"])

        # Сохраняем DataFrame в CSV
        csv_file_path = "kpi_results.csv"
        df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
        print(f"Результаты сохранены в {csv_file_path}")
    except Exception as e:
        print(f"Ошибка при сохранении в CSV: {e}")

def list_current_directory():
    """Выводит текущий путь и список файлов в текущей директории."""
    current_path = os.getcwd()
    print(f"Текущий путь: {current_path}")
    print("Содержимое текущей директории:")
    for item in os.listdir(current_path):
        print(f"  - {item}")

def analyze_kpi():
    """Функция для анализа KPI."""
    list_current_directory()  # Выводим текущий путь и список файлов
    file_path = input("Введите путь к CSV файлу для анализа: ")
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                print("Файл не содержит данных.")
                return

            # Проверяем наличие необходимых столбцов
            required_columns = ['time', 'date', 'place', 'id']
            if not all(column in df.columns for column in required_columns):
                print(f"Файл должен содержать следующие столбцы: {', '.join(required_columns)}")
                return

            process_data(df)
        except Exception as e:
            print(f"Не удалось загрузить файл: {e}")
    else:
        print("Указанный файл не существует.")

def get_db_info(filename, section):
    parser = configparser.ConfigParser()
    parser.read(filename)
    db_info = {}
    if parser.has_section(section):
        key_val_tuple = parser.items(section)
        for item in key_val_tuple:
            db_info[item[0]] = item[1]
    return db_info

def connect(params_dict):
    conn = None
    try:
        print("Подключение к базе данных PostgreSQL...")
        conn = psycopg2.connect(**params_dict)
        print("Подключение прошло успешно!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка: {error}")
        return None
    return conn

def postgresql_to_dataframe(conn, select_query, column_names):
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка: {error}")
        cursor.close()
        return None
    tuples = cursor.fetchall()
    cursor.close()
    df = pd.DataFrame(tuples, columns=column_names)
    return df

# Функция для экспорта данных в CSV
def export_to_csv():
    try:
        conn = connect(param_dict)
        if conn is None:
            return
        cur = conn.cursor()

        # Выполнение запроса
        cur.execute("""
            SELECT
                k.id,
                k.date,
                k.number,
                k.place,
                m.amount,
                k.t_c,
                k.branch,
                s.time as start,
                e.time as end,
                (e.time - s.time) as time
            FROM
                kupiflakon k
                LEFT JOIN money m ON k.id = m.id
                LEFT JOIN time_start s ON k.id = s.id
                LEFT JOIN time_end e ON k.id = e.id
            WHERE
                k.date BETWEEN DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
                          AND (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day')
                AND (e.time - s.time) < INTERVAL '2 hours'
        """)

        # Генерация имени файла с текущей датой
        output_file = f"/home/max/kpi_{datetime.now().strftime('%Y-%m-%d')}.csv"

        # Запись в CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([desc[0] for desc in cur.description])  # Заголовки
            writer.writerows(cur.fetchall())

        print(f"Данные успешно экспортированы в {output_file}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

# Функции из отдельных скриптов
def number_search():
    try:
        conn = connect(param_dict)
        if conn is None:
            return
        column_names = ["ID", "Дата", "Номер", "Место", "ТК", "Филиал"]
        n = int(input("Введите номер заказа: "))
        df = postgresql_to_dataframe(conn, f"SELECT * FROM kupiflakon WHERE number = {n}", column_names)
        if df is None or len(df) == 0:
            print("Нет данных")
        else:
            print(df.query('Номер == @n'))
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
      if conn:
        conn.close()

def orders_today():
    try:
        conn = connect(param_dict)
        if conn is None:
            return
        column_names = ["ID", "Дата", "Номер", "Место", "ТК", "Филиал"]
        k = int(input("Количество с конца: "))
        df = postgresql_to_dataframe(conn, "SELECT * FROM kupiflakon WHERE date = CURRENT_DATE", column_names)
        if df is None:
            print("Нет данных")
            return
        if len(df) > 30:
          print(df.tail(k))
        elif len(df) > 0:
            print(df.tail(k))
        else:
            print("Нет данных")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
      if conn:
        conn.close()

def time_end():
    try:
        conn = connect(param_dict)
        if conn is None:
            return
        with conn.cursor() as db_cursor:
          db_cursor.execute("SELECT id, number, t_c FROM kupiflakon WHERE date = CURRENT_DATE")
          a = int(input("Введите id: "))
          db_cursor.execute("INSERT INTO time_end (id, time) VALUES (%s, CURRENT_TIMESTAMP)", [a])
        conn.commit()
        print("Успешная вставка в time_end")
    except Exception as e:
      print(f"Ошибка ввода данных: {e}")
      conn.rollback()
    finally:
      if conn:
        conn.close()

def time_start():
    try:
      conn = connect(param_dict)
      if conn is None:
            return
      with conn.cursor() as db_cursor:
        db_cursor.execute("SELECT id, number, t_c FROM kupiflakon WHERE date = CURRENT_DATE")
        a = int(input("Введите id: "))
        db_cursor.execute("INSERT INTO time_start (id, time) VALUES (%s, CURRENT_TIMESTAMP)", [a])
      conn.commit()
      print("Успешная вставка в time_start")
    except Exception as e:
      print(f"Ошибка ввода данных: {e}")
      conn.rollback()
    finally:
        if conn:
            conn.close()

def money_records():
  filename = 'db_info.ini'
  section = 'postgres-sample-db'
  db_info = get_db_info(filename, section)

  try:
    with psycopg2.connect(**db_info) as db_connection:
        with db_connection.cursor() as db_cursor:
            db_cursor.execute("SELECT id, number, t_c FROM kupiflakon WHERE date = CURRENT_DATE")
            x = db_cursor.fetchall()
            print(str(x).replace('), (', ',\n'))

            x = int(input("Введите количество заказов: "))
            for i in range(x):
              a = int(input("Введите id: "))
              b = int(input("Введите сумму заказа: "))
              d = int(input("Введите сумму доставки: "))
              insert_record = 'INSERT INTO money (id, amount) VALUES (%s, %s)'
              insert_value = (a, b - d)
              db_cursor.execute(insert_record, insert_value)
        db_connection.commit()
        print("Успешная вставка в money")
  except Exception as e:
    print(f"Ошибка ввода данных: {e}")
  finally:
    if db_connection:
      db_connection.close()

def kupiflakon_insert():
    filename = 'db_info.ini'
    section = 'postgres-sample-db'
    db_info = get_db_info(filename, section)

    try:
        with psycopg2.connect(**db_info) as db_connection:
            with db_connection.cursor() as db_cursor:
                x = int(input("Введите количество заказов: "))
                for i in range(x):
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    n = input("Номер заказа: ")
                    if n == "":
                       n = None
                    else:
                      n = int(n)
                    num = int(input('Количество: '))
                    if num == "":
                      num = None
                    else:
                      num = str(num).zfill(5)
                    print("""
Выберите ТК:
    1 - Boxberry
    2 - ПЭК
    3 - Самовывоз
    4 - Деловые линии
    5 - Почта России
    6 - Yandex Market
    7 - Mega Market
    8 - AliExpress
    9 - Образцы
    10 - OZON_FBS
    11 - Ярмарка Мастеров
    12 - CDEK
    13 - WB_FBS
    14 - DPD
    15 - Бийск
    --------------
    16 - OZON_FBO
    17 - WB_FBO
""")
                    list_tk = [
    'Boxberry', 'ПЭК', 'Самовывоз', 'Деловые линии', 
    'Почта России', 'Yandex Market', 'Mega Market', 
    'AliExpress', 'Образцы', 'OZON_FBS', 'Ярмарка Мастеров', 
    'CDEK', 'WB_FBS', 'DPD', 'Бийск', 'OZON_FBO', 'WB_FBO'
                    ]
                    tk = int(input("TK: "))
                    tk = list_tk[tk-1]
                    print("""
Выберите подразделение:
    1 - Маркетплейс
    2 - Купи-Флакон
    3 - Pack Stage
    ----
    """)
                    list_branch = [
                        'MP', 'KF', 'Pack Stage'
                    ]
                    b = int(input("Branch: "))
                    company = list_branch[b-1]
                    
                    insert_record = 'INSERT INTO kupiflakon (date, number, place, t_c, branch) VALUES (%s, %s, %s, %s, %s)'
                    insert_value = (date_str, n, num, tk, company)
                    db_cursor.execute(insert_record, insert_value)
            db_connection.commit()
            print("Успешная вставка в kupiflakon")
    except Exception as e:
        print(f"Ошибка ввода данных: {e}")
        db_connection.rollback()
    finally:
      if db_connection:
            db_connection.close()

def info_order():
    try:
        conn = connect(param_dict)
        if conn is None:
            return
        column_names = ["ID", "Дата", "Номер", "Мест", "Сумма", "ТК", "Филиал"]
        date_start = input("Введите начальную дату в формате ГГГГ-ММ-ДД: ")
        year_s, month_s, day_s = [int(item) for item in date_start.split('-')]
        date_start = datetime(year_s, month_s, day_s)
        
        date_end = input("Введите конечную дату в формате ГГГГ-ММ-ДД (если нужен один день нажмите enter): ")
        if date_end:
          year_e, month_e, day_e = [int(item) for item in date_end.split('-')]
          date_end = datetime(year_e, month_e, day_e)
          df = postgresql_to_dataframe(conn, f"SELECT k.id, k.date, k.number, k.place, m.amount, k.t_c, k.branch FROM kupiflakon k LEFT JOIN money m ON k.id = m.id WHERE k.date BETWEEN '{date_start}' AND '{date_end}'", column_names)
        else:
           df = postgresql_to_dataframe(conn, f"SELECT k.id, k.date, k.number, k.place, m.amount, k.t_c, k.branch FROM kupiflakon k LEFT JOIN money m ON k.id = m.id WHERE k.date = '{date_start}'", column_names)
        if df is None:
            print("No data")
            return
        print("----------------------------------------------")
        print('Итого:' ,df.Сумма.sum(), '₽')
        print('Количество заказов:', df.Мест.shape[0], 'шт')
        print('Сумма в среднем за один заказ:', round(np.mean(df.Сумма)), '₽')
        print("----------------------------------------------")
        print("Количество заказов по Купи-Флакон")
        print(df.query('Филиал == "KF"').groupby('ТК', as_index=False).agg({'Мест': 'count'}).sort_values('Мест', ascending=False))
        print("Количество заказов по Маркетплейсам")
        print(df.query('Филиал == "MP"').groupby('ТК', as_index=False).agg({'Мест': 'sum'}).sort_values('Мест', ascending=False))
        print("----------------------------------------------")
        print("Сумма заказов по Купи-Флакон")
        print(df.query('Филиал == "KF"').groupby('ТК', as_index=False).agg({'Сумма': 'sum'}).sort_values('Сумма', ascending=False))
        print("Сумма заказов по Маркетплейсам")
        print(df.query('Филиал == "MP"').groupby('ТК', as_index=False).agg({'Сумма': 'sum'}).sort_values('Сумма', ascending=False))
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if conn:
            conn.close()

def update_kupiflakon():
  filename = 'db_info.ini'
  section = 'postgres-sample-db'
  db_info = get_db_info(filename, section)

  try:
    with psycopg2.connect(**db_info) as db_connection:
      with db_connection.cursor() as db_cursor:
          db_cursor.execute("SELECT * FROM kupiflakon WHERE date = CURRENT_DATE;")
          print(str(db_cursor.fetchall()).replace('), (', ',\n'))
          
          i = int(input("Введите id: "))
          a = int(input("Введите новое количество: "))
          db_cursor.execute("UPDATE kupiflakon SET place = %s WHERE date = CURRENT_DATE AND id = %s;", (a, i))
      db_connection.commit()
      print("Успешная вставка в kupiflakon")
  except Exception as e:
      print(f"Ошибка ввода данных: {e}")
      db_connection.rollback()
  finally:
    if db_connection:
        db_connection.close()

def jambs_insert():
  filename = 'db_info.ini'
  section = 'postgres-sample-db'
  db_info = get_db_info(filename, section)
  try:
      with psycopg2.connect(**db_info) as db_connection:
          with db_connection.cursor() as db_cursor:
              n = int(input("Введите номер заказа: "))
              db_cursor.execute('SELECT * FROM kupiflakon WHERE number = %s;', (n,))
              print(str(db_cursor.fetchall()))
              i = int(input("Введите id: "))
              p = input("Количество мест: ")
              d = datetime.now().strftime('%y-%m-%d')
              print("""
                  Выберете статус:
                      1 - Ошибка
                      2 - Недовложение
                      3 - Лишнее
                      4 - Возврат
                      5 - Повтор
                      6 - Обмен
                  """)
              ones = ['Ошибка', 'Недовложение', 'Лишнее', 'Возврат', 'Повтор', 'Обмен']
              j = int(input("Статус: "))
              word = ones[j-1]
              insert_record = 'INSERT INTO jambs (id, jamb, place, date) VALUES (%s, %s, %s, %s)'
              insert_value = (i, word, p, d)
              db_cursor.execute(insert_record, insert_value)
          db_connection.commit()
          print("Успешная вставка в jambs")
  except Exception as e:
      print(f"Ошибка ввода данных: {e}")
      db_connection.rollback()
  finally:
      if db_connection:
          db_connection.close()

def duplicates_search():
    try:
      conn = connect(param_dict)
      if conn is None:
        return
      column_names = ['number', 'count']
      df = postgresql_to_dataframe(conn,"SELECT number, COUNT(*) FROM kupiflakon GROUP BY number HAVING COUNT(*) > 1 and number IS NOT NULL", column_names)
      if df is None:
          print("Нет данных")
      elif len(df) > 0:
        print(df.head())
      else:
        print("Нет данных")
    except Exception as e:
      print(f"Произошла ошибка: {e}")
    finally:
      if conn:
        conn.close()

# Main execution
if __name__ == "__main__":
  while True:
      print("""
Выберите действие:
   
    1 - Поиск заказа по номеру
    2 - Показать заказы за сегодня
    3 - Конец сборки заказа
    4 - Начало сборки заказа
    5 - Внести данные в money
    6 - Внести данные в kupiflakon
    7 - Статистика определенный период
    8 - Обновить данные по местам
    9 - Занести данные в jambs
    10 - Поиск дубликатов
    11 - Экспорт данных в CSV
    12 - Анализ KPI
    0 - Выход

""")
      choice = input("Ваш выбор: ")
      if choice == "1":
          number_search()
      elif choice == "2":
          orders_today()
      elif choice == "3":
         time_end()
      elif choice == "4":
        time_start()
      elif choice == "5":
        money_records()
      elif choice == "6":
        kupiflakon_insert()
      elif choice == "7":
        info_order()
      elif choice == "8":
        update_kupiflakon()
      elif choice == "9":
        jambs_insert()
      elif choice == "10":
          duplicates_search()
      elif choice == "11":
          export_to_csv()
      elif choice == "12":
          analyze_kpi()
      elif choice == "0":
          break
      else:
          print("Неверный выбор. Попробуйте снова.")
print("Соединение с PostgreSQL закрыто")