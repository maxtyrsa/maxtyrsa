import vk_api
from vk_api.exceptions import ApiError
import random
import json
import time
import logging
import os
from threading import Thread
import webbrowser
from datetime import datetime
from collections import Counter
from tqdm import tqdm  # Импорт tqdm

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vk_unified_script.log"),  # Логи будут сохраняться в файл
        logging.StreamHandler()  # Логи будут выводиться в консоль
    ]
)

logger = logging.getLogger(__name__)

# Логирование ошибок в отдельный файл
error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler("error.log")
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
error_logger.addHandler(error_handler)


class Statistics:
    def __init__(self):
        self.users_found = 0
        self.users_filtered = 0
        self.friends_added = 0
        self.messages_sent = 0
        self.posts_liked = 0
        self.posts_commented = 0

    def increment(self, stat_name):
        """Увеличивает счетчик статистики."""
        if hasattr(self, stat_name):
            setattr(self, stat_name, getattr(self, stat_name) + 1)

    def add(self, stat_name, value):
        """Увеличивает счетчик статистики на определенное значение."""
        if hasattr(self, stat_name):
            setattr(self, stat_name, getattr(self, stat_name) + value)


    def display(self):
        """Выводит статистику."""
        print("\nСтатистика:")
        print(f"  Найдено пользователей: {self.users_found}")
        print(f"  Отфильтровано пользователей: {self.users_filtered}")
        print(f"  Добавлено в друзья: {self.friends_added}")
        print(f"  Отправлено сообщений: {self.messages_sent}")
        print(f"  Лайков поставлено: {self.posts_liked}")
        print(f"  Комментариев добавлено: {self.posts_commented}")


    def save_to_json(self, filename="statistics.json"):
        """Сохраняет статистику в JSON файл."""
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self.__dict__, file, indent=4)
            logger.info(f"Статистика сохранена в файл: {filename}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении статистики в файл: {e}")

    def load_from_json(self, filename="statistics.json"):
        """Загружает статистику из JSON файла."""
        if os.path.exists(filename): #проверка файла
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.__dict__.update(data)
                logger.info(f"Статистика загружена из файла: {filename}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке статистики из файла: {e}")


def get_account_folder(account_name):
    """Возвращает путь к папке аккаунта. Если папка не существует, создает её."""
    folder_name = f"{account_name}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name


def load_token_from_json(account_name, filename="config.json"):
    """Загрузка токена из JSON файла."""
    folder = get_account_folder(account_name)
    file_path = os.path.join(folder, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            config = json.load(file)
            return config.get("access_token", "")
    except Exception as e:
        logger.error(f"Ошибка при загрузке токена из файла: {e}")
        return ""


def save_token_to_json(token, account_name, filename="config.json"):
    """Сохранение токена в JSON файл."""
    folder = get_account_folder(account_name)
    file_path = os.path.join(folder, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump({"access_token": token}, file, indent=4)
        logger.info(f"Токен успешно обновлен в файле {file_path}.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении токена в файл: {e}")


def extract_token(token_string):
    """Извлечение токена из строки, полученной после авторизации."""
    try:
        token_start = token_string.find("access_token=")
        if token_start == -1:
            raise ValueError("Неверный формат строки: отсутствует 'access_token='.")
        token_start += len("access_token=")
        token_end = token_string.find("&", token_start)
        if token_end == -1:
            raise ValueError("Неверный формат строки: отсутствует '&' после токена.")
        token = token_string[token_start:token_end]
        return token
    except Exception as e:
        logger.error(f"Ошибка при извлечении токена: {e}")
        return None


def get_auth_url():
    """Возвращает URL для авторизации через VK OAuth."""
    app_id = "6287487"  # Замените на ваш app_id
    redirect_uri = "https://oauth.vk.com/blank.html"  # Стандартный redirect_uri
    scope = "friends,photos,messages,wall,groups"  # Добавлено groups
    display = "page"  # Отображение в виде страницы
    response_type = "token"  # Тип ответа — токен
    v = "5.199"  # Версия API VK

    auth_url = (
        f"https://oauth.vk.com/authorize?"
        f"client_id={app_id}&"
        f"display={display}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type={response_type}&"
        f"v={v}"
    )
    return auth_url


def update_token(account_name):
    """Обновление токена и сохранение его в config.json."""
    print("\nДля обновления токена выполните следующие шаги:")
    print("1. Перейдите по ссылке ниже, чтобы авторизоваться в VK.")
    print("2. После авторизации вы будете перенаправлены на страницу с токеном.")
    print("3. Скопируйте URL этой страницы и вставьте его здесь.")

    auth_url = get_auth_url()
    print(f"\nСсылка для авторизации: {auth_url}")
    webbrowser.open(auth_url)  # Открываем ссылку в браузере

    token_string = input("\nВведите URL страницы с токеном: ")
    token = extract_token(token_string)
    
    if token:
        save_token_to_json(token, account_name)
        logger.info("Токен успешно обновлен.")
    else:
        logger.error("Не удалось извлечь токен из строки.")


def load_processed_ids(account_name, filename="processed_ids.txt"):
    """Загрузка уже обработанных ID пользователей из файла."""
    folder = get_account_folder(account_name)
    file_path = os.path.join(folder, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return {int(line.strip()) for line in file}
    except FileNotFoundError:
        return set()


def save_processed_id(user_id, account_name, filename="processed_ids.txt"):
    """Сохранение ID пользователя в файл обработанных ID."""
    folder = get_account_folder(account_name)
    file_path = os.path.join(folder, filename)
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"{user_id}\n")
    except Exception as e:
        logger.error(f"Ошибка при сохранении ID пользователя {user_id}: {e}")


def auth_vk(access_token):
    """Авторизация в VK API."""
    try:
        vk_session = vk_api.VkApi(token=access_token)
        vk = vk_session.get_api()
        logger.info("Успешная авторизация в VK API.")
        return vk
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        raise


def get_city_id(vk, city_name):
    """Получение ID города по названию."""
    try:
        response = vk.database.getCities(country_id=1, q=city_name, count=10)
        if response.get("items"):
            logger.info(f"Найдены города по запросу '{city_name}':")
            for city in response["items"]:
                logger.info(f"ID: {city['id']}, Название: {city['title']}")
            return response["items"][0]["id"]
        else:
            logger.warning(f"Город '{city_name}' не найден.")
            return 0
    except ApiError as e:
        logger.error(f"Ошибка при поиске города: {e}")
        return 0


def get_user_groups(vk, user_id):
    """Получение списка групп пользователя."""
    try:
        response = vk.groups.get(user_id=user_id, extended=1, fields="name,id")
        return response.get("items", [])
    except ApiError as e:
        error_logger.error(f"Ошибка при получении групп пользователя {user_id}: {e}")
        return []
    

def check_user_group_themes(vk, user_id, group_themes):
    """Проверка, есть ли у пользователя группы с заданной тематикой."""
    user_groups = get_user_groups(vk, user_id)
    if not user_groups:
        return False

    for group in user_groups:
       if any(theme.lower() in group.get('name', '').lower() for theme in group_themes):
         return True
    return False


def search_users(vk, criteria, account_name, group_themes=None, statistics=None):
    """Поиск пользователей по критериям."""
    try:
        response = vk.users.search(
            q=criteria.get("q", ""),
            sex=criteria.get("sex", 0),
            age_from=criteria.get("age_from", 0),
            age_to=criteria.get("age_to", 0),
            city=criteria.get("city", 0),
            country=criteria.get("country", 0),
            hometown=criteria.get("hometown", ""),
            has_photo=criteria.get("has_photo", 0),
            online=criteria.get("online", 0),
            count=criteria.get("count", 10),
            offset=criteria.get("offset", 0),
            fields="id,first_name,last_name,can_write_private_message,can_send_friend_request,interests,books,movies,music,activities"
        )
        processed_ids = load_processed_ids(account_name)
        filtered_users = []
        
        users_list = response.get("items", [])
        
        if statistics:
            statistics.add("users_found", len(users_list)) # Записываем количество найденных

        with tqdm(total=len(users_list), desc="Обработка пользователей") as progress_bar:
            for user in users_list:
              if user["id"] not in processed_ids:
                 if group_themes:
                      try:
                         if check_user_group_themes(vk, user["id"], group_themes):
                            filtered_users.append(user)
                      except ApiError as e:
                            if e.code == 30: # Код 30 - приватный профиль
                                error_logger.error(f"Пропущен пользователь {user['id']} из-за приватного профиля.")
                                continue  # Пропустить пользователя, если профиль приватный
                            else:
                                error_logger.error(f"Ошибка при проверке групп пользователя {user['id']}: {e}")
                 else:
                    filtered_users.append(user)
              progress_bar.update(1)
        
        if statistics:
            statistics.add("users_filtered", len(filtered_users)) # Записываем количество отфильтрованных
        return filtered_users
            

    except ApiError as e:
        logger.error(f"Ошибка при поиске пользователей: {e}")
        return []


def filter_users(users):
    """Фильтрация пользователей: оставляем только тех, кому можно писать и добавлять в друзья."""
    filtered_users = []
    for user in users:
        if user.get("can_write_private_message", 0) == 1 and user.get("can_send_friend_request", 0) == 1:
            filtered_users.append(user)
    return filtered_users


def save_user_ids_to_file(user_ids, account_name, filename="user_ids.txt"):
    """Сохранение ID пользователей в текстовый файл."""
    folder = get_account_folder(account_name)
    file_path = os.path.join(folder, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            for user_id in user_ids:
                file.write(f"{user_id}\n")
        logger.info(f"ID пользователей сохранены в файл: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении в файл: {e}")


def add_friends(vk, user_ids, account_name, delay=5, statistics=None):
    """Добавление пользователей в друзья с задержкой между запросами."""
    with tqdm(total=len(user_ids), desc="Добавление в друзья") as progress_bar:
        for user_id in user_ids:
            try:
                response = vk.friends.add(user_id=user_id)
                if response == 1:
                    logger.info(f"Запрос на добавление в друзья пользователю {user_id} отправлен.")
                    save_processed_id(user_id, account_name)
                    if statistics:
                       statistics.increment("friends_added") # Записываем количество добавленных друзей
                else:
                    logger.warning(f"Не удалось отправить запрос пользователю {user_id}.")
            except ApiError as e:
                logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
            finally:
                logger.info(f"Ожидание {delay} секунд перед следующим запросом...")
                time.sleep(delay)
                progress_bar.update(1)


def send_message(vk, user_id, message, account_name, statistics=None):
    """Отправка сообщения пользователю."""
    try:
        vk.messages.send(user_id=user_id, message=message, random_id=0)
        logger.info(f"Сообщение отправлено пользователю {user_id}.")
        save_processed_id(user_id, account_name)
        save_sent_message_id(user_id, account_name)
        if statistics:
           statistics.increment("messages_sent") # Записываем количество отправленных сообщений
    except ApiError as e:
        error_logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}. Код ошибки: {e.code}, Описание: {e.description}")
        if e.code == 901: # Нельзя отправить сообщение пользователю
            logger.warning(f"Нельзя отправить сообщение пользователю {user_id}. Вероятно, он ограничил круг людей, которые могут ему писать. Пропускаем.")
            save_processed_id(user_id, account_name)
            save_sent_message_id(user_id, account_name)
        elif e.code == 900: # Слишком много сообщений
            logger.warning(f"Слишком много сообщений. Ожидание перед отправкой {user_id}")
            time.sleep(60)
        else:
            time.sleep(random.uniform(5,10)) # Небольшая задержка
    except Exception as e:
        error_logger.error(f"Непредвиденная ошибка при отправке сообщения пользователю {user_id}: {e}")


def get_new_friends(vk):
    """Получение списка новых друзей."""
    try:
        friends = vk.friends.get(order="hints", count=1000, fields="id")
        logger.info("Список друзей успешно получен.")
        return friends.get("items", [])
    except ApiError as e:
        logger.error(f"Ошибка при получении списка друзей: {e}")
        return []


def load_sent_message_ids(account_name, filename="sent_messages.txt"):
    """Загрузка ID пользователей, которым уже отправлено сообщение."""
    folder = get_account_folder(account_name)
    file_path = os.path.join(folder, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return {int(line.strip()) for line in file}
    except FileNotFoundError:
        return set()


def save_sent_message_id(user_id, account_name, filename="sent_messages.txt"):
    """Сохранение ID пользователя в файл отправленных сообщений."""
    folder = get_account_folder(account_name)
    file_path = os.path.join(folder, filename)
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"{user_id}\n")
    except Exception as e:
        logger.error(f"Ошибка при сохранении ID пользователя {user_id}: {e}")


def load_list_from_file(filename):
    """Загрузка списка строк из файла."""
    try:
      with open(filename, "r", encoding="utf-8") as file:
         return [line.strip() for line in file]
    except FileNotFoundError:
         return []


def save_list_to_file(data, filename):
     """Сохранение списка строк в файл."""
     try:
        with open(filename, "w", encoding="utf-8") as file:
          for item in data:
            file.write(f"{item}\n")
        logger.info(f"Данные успешно сохранены в файл: {filename}")
     except Exception as e:
        logger.error(f"Ошибка при сохранении в файл {filename}: {e}")


def load_group_themes_from_file(filename="group_themes.txt"):
    """Загрузка тематик групп из файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        return []

def search_and_save_users(vk, account_name, statistics=None):
    """Поиск пользователей и сохранение их ID в файл."""
    cities = load_list_from_file("cities.txt")
    if not cities:
        logger.warning("Файл cities.txt не найден. Пожалуйста, создайте его и добавьте города.")
        cities = [] # Пустой список

    # Загрузка тематик из файла
    group_themes_list = load_group_themes_from_file()

    # Вывод списка доступных тематик
    if group_themes_list:
         print("Доступные тематики:")
         for i, theme in enumerate(group_themes_list):
             print(f"{i+1}. {theme}")
    
    # Запрос на выбор тематик
    while True:
       group_themes_choice_input = input("Выберите номера тематик через запятую (или оставьте пустым для поиска без тематик): ").strip()
       if not group_themes_choice_input:
         group_themes = None
         break
       try:
         group_themes_choice_indexes = [int(index.strip()) - 1 for index in group_themes_choice_input.split(',')]
         if any(index < 0 or index >= len(group_themes_list) for index in group_themes_choice_indexes):
            print("Некорректный выбор тематик. Попробуйте снова.")
            continue
         group_themes = [group_themes_list[index] for index in group_themes_choice_indexes]
         break
       except ValueError:
         print("Некорректный ввод. Введите номера через запятую.")
    
    if group_themes:
        logger.info(f"Выбраны тематики: {', '.join(group_themes)}")
        save_list_to_file(group_themes, "group_themes.txt")


    city_choice = input("Выберите способ указания города:\n1. Ввести вручную\n2. Случайный выбор из файла cities.txt\nВведите 1 или 2: ")

    if city_choice == "1":
      city_name = input("Введите название города для поиска: ")
      city_id = get_city_id(vk, city_name)
    elif city_choice == "2":
         if cities:
          city_name = random.choice(cities)
          logger.info(f"Выбран случайный город из файла: {city_name}")
          city_id = get_city_id(vk, city_name)
         else:
           logger.error("Файл cities.txt не найден. Пожалуйста, введите город вручную.")
           city_name = input("Введите название города для поиска: ")
           city_id = get_city_id(vk, city_name)
    else:
        logger.error("Неверный выбор. Пожалуйста, введите 1 или 2.")
        return
    
    if not city_id:
        logger.error(f"Город '{city_name}' не найден.")
        return

    criteria = {
        "sex": int(input("Введите пол (1 — женский, 2 — мужской, 0 — любой): ")),
        "age_from": int(input("Введите минимальный возраст: ")),
        "age_to": int(input("Введите максимальный возраст: ")),
        "city": city_id,
        "has_photo": 1,  # Только с фото
        "online": 1, # Только онлайн
        "count": int(input("Введите количество пользователей для поиска: ")),
        "offset": 0
    }
    logger.info("Начало поиска пользователей...")
    users = search_users(vk, criteria, account_name, group_themes, statistics)
    logger.info(f"Найдено {len(users)} пользователей.")

    filtered_users = filter_users(users)
    logger.info(f"После фильтрации осталось {len(filtered_users)} пользователей.")

    user_ids = [user["id"] for user in filtered_users]
    save_user_ids_to_file(user_ids, account_name, "user_ids.txt")


def add_friends_from_file(vk, account_name, statistics=None):
    """Добавление друзей из файла user_ids.txt."""
    folder = get_account_folder(account_name)
    file_path = os.path.join(folder, "user_ids.txt")
    try:
        with open(file_path, "r") as file:
            user_ids = [int(line.strip()) for line in file]
            logger.info(f"Загружено {len(user_ids)} ID пользователей из файла {file_path}.")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {e}")
        return

    delay = int(input("Введите задержку между запросами (в секундах): "))
    logger.info("Начало добавления друзей...")
    add_friends(vk, user_ids, account_name, delay=delay, statistics=statistics)
    logger.info("Добавление друзей завершено.")


def generate_compliment(user):
    """Генерация комплимента на основе профиля пользователя."""
    compliments = []
    
    interests = user.get("interests", "").lower()
    books = user.get("books", "").lower()
    movies = user.get("movies", "").lower()
    music = user.get("music", "").lower()
    activities = user.get("activities", "").lower()

    common_interests = load_list_from_file("interests.txt")
    common_books = load_list_from_file("books.txt")
    common_movies = load_list_from_file("movies.txt")
    common_music = load_list_from_file("music.txt")
    common_activities = load_list_from_file("activities.txt")

    if interests and common_interests:
       interests_list = [interest.strip() for interest in interests.split(',')]
       user_common_interests = [interest for interest in interests_list if interest in common_interests]
       if user_common_interests:
            compliments.append(f"Интересно, у тебя похожие интересы со мной! Здорово, что ты интересуешься {', '.join(user_common_interests)}!")
       else:
           compliments.append(f"Ваши увлечения, такие как {interests}, кажутся очень интересными!")

    if books and common_books:
       books_list = [book.strip() for book in books.split(',')]
       user_common_books = [book for book in books_list if book in common_books]
       if user_common_books:
            compliments.append(f"Отличный вкус в литературе! Я тоже люблю {', '.join(user_common_books)}!")
       else:
           compliments.append(f"Заметно, что у вас хороший вкус в литературе: {books}!")

    if movies and common_movies:
        movies_list = [movie.strip() for movie in movies.split(',')]
        user_common_movies = [movie for movie in movies_list if movie in common_movies]
        if user_common_movies:
            compliments.append(f"Класс! У нас есть общие предпочтения в кино, особенно люблю {', '.join(user_common_movies)}!")
        else:
             compliments.append(f"Я вижу, у вас интересные предпочтения в кино: {movies}!")

    if music and common_music:
         music_list = [music_item.strip() for music_item in music.split(',')]
         user_common_music = [music_item for music_item in music_list if music_item in common_music]
         if user_common_music:
              compliments.append(f"У нас похожий музыкальный вкус! Обожаю {', '.join(user_common_music)}!")
         else:
              compliments.append(f"Приятно видеть, что вы слушаете {music}!")
    
    if activities and common_activities:
       activities_list = [activity.strip() for activity in activities.split(',')]
       user_common_activities = [activity for activity in activities_list if activity in common_activities]
       if user_common_activities:
            compliments.append(f"Активный образ жизни это здорово! Рад видеть, что ты занимаешься {', '.join(user_common_activities)}!")
       else:
           compliments.append(f"Заметил, вы занимаетесь {activities} - это здорово!")

    if not compliments:
        compliments.append("Мне понравился ваш профиль, вы кажетесь интересным человеком!")

    return random.choice(compliments)


def send_messages_to_new_friends(vk, account_name, statistics=None):
    """Отправка сообщений новым друзьям с упоминанием их имени и комплиментом."""
    logger.info("Ожидание новых друзей...")
    sent_message_ids = load_sent_message_ids(account_name)

    # Инициализация current_friend_ids - получаем список друзей
    current_friends = get_new_friends(vk)
    current_friend_ids = {friend["id"] for friend in current_friends}

    while True:
        try:
            # Получаем список текущих друзей в текущем цикле
            new_friends = get_new_friends(vk)
            new_friend_ids = {friend["id"] for friend in new_friends}

            # Находим новых друзей, которые не были обработаны
            new_friends_added = (new_friend_ids - current_friend_ids) - sent_message_ids

            if new_friends_added:
                logger.info(f"Найдены новые друзья: {new_friends_added}")
            else:
                logger.info("Новых друзей не найдено.")

            for user_id in new_friends_added:
                user_info = vk.users.get(user_ids=user_id, fields="first_name,interests,books,movies,music,activities")[0]
                user_name = user_info["first_name"]
                compliment = generate_compliment(user_info)
                message = f"Привет, {user_name}! 🤗 {compliment} Есть отличное предложение: удалённая работа в банке с зарплатой от 3 тыс. рублей в день. Никаких сложностей — только ваш ноутбук и интернет. Хотите узнать больше?"
                send_message(vk, user_id, message, account_name, statistics)

            # Обновляем current_friend_ids для следующей итерации
            current_friend_ids = new_friend_ids
            time.sleep(60)  # Проверка каждую минуту

        except Exception as e:
            logger.error(f"Ошибка в работе скрипта: {e}")
            time.sleep(60)



def is_token_valid(vk):
    """Проверка, действителен ли токен."""
    try:
        vk.users.get()
        return True
    except ApiError as e:
        if e.code == 5:  # Ошибка авторизации
            return False
        else:
            raise  # Другие ошибки

def send_messages_to_specific_users(vk, account_name, statistics=None):
    """Отправка сообщений определенным пользователям или друзьям."""
    message = input("Введите текст сообщения для отправки: ")
    user_ids_source = input("Выберите источник ID пользователей:\n1. Файл txt\n2. Ввод через запятую\nВведите 1 или 2: ")

    if user_ids_source == "1":
        filename = input("Введите имя файла с ID пользователей (в формате txt): ")
        folder = get_account_folder(account_name)
        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            logger.error(f"Файл '{file_path}' не найден.")
            return
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                user_ids = [int(line.strip()) for line in file if line.strip().isdigit()]
        except Exception as e:
            logger.error(f"Ошибка при чтении файла '{file_path}': {e}")
            return
        if not user_ids:
            logger.warning(f"Файл '{file_path}' пуст или содержит некорректные данные.")
            return

    elif user_ids_source == "2":
        user_input = input("Введите ID пользователей (через запятую): ").strip()
        try:
            user_ids = [int(user_id.strip()) for user_id in user_input.split(",") if user_id.strip().isdigit()]
        except ValueError:
            logger.error("Некорректный формат ID пользователей. Введите ID через запятую.")
            return
        if not user_ids:
            logger.warning("Список ID пуст.")
            return

    else:
        logger.error("Неверный выбор источника ID. Введите 1 или 2.")
        return

    with tqdm(total=len(user_ids), desc="Отправка сообщений") as progress_bar:
        for user_id in user_ids:
          send_message(vk, user_id, message, account_name, statistics)
          progress_bar.update(1)

def process_friends_posts(vk, my_id, like=True, comment=True, statistics=None):
    """Обработка постов друзей: лайки и/или комментарии."""
    try:
        response = vk.newsfeed.get(filters='post', count=50) # Максимум 200
        posts = response.get('items', [])
        logger.info(f"Получено {len(posts)} постов от друзей.")

        with tqdm(total=len(posts), desc="Обработка постов") as progress_bar:
            for post in posts:
              post_id = post['post_id']
              owner_id = post['owner_id']
              if owner_id == my_id:
                continue

              try:
                  if like:
                      vk.likes.add(type='post', owner_id=owner_id, item_id=post_id)
                      logger.info(f"Лайк поставлен посту {post_id} пользователя {owner_id}")
                      if statistics:
                         statistics.increment("posts_liked") # Записываем количество поставленных лайков
                  if comment:
                      comment_text = generate_comment()  # Генерируем случайный комментарий
                      vk.wall.createComment(owner_id=owner_id, post_id=post_id, message=comment_text)
                      logger.info(f"Комментарий '{comment_text}' добавлен к посту {post_id} пользователя {owner_id}")
                      if statistics:
                        statistics.increment("posts_commented") # Записываем количество добавленных комментариев
                      
                  time.sleep(random.uniform(3, 8))  # Задержка между постами
              except ApiError as e:
                    error_logger.error(f"Ошибка при обработке поста {post_id} пользователя {owner_id}: {e}")
              finally:
                  progress_bar.update(1)

    except ApiError as e:
          error_logger.error(f"Ошибка при получении постов друзей: {e}")


def generate_comment():
    """Генерация случайного комментария."""
    comments = [
        "Отличный пост!",
        "Интересно!",
        "👍",
        "Здорово!",
        "Круто!",
        "Хорошо сказано!",
        "Согласен!",
        "Полезная информация!",
        "Спасибо!",
        "Супер!",
        "Класс!"
    ]
    return random.choice(comments)

# Создаем экземпляр класса Statistics глобально
statistics = Statistics()

def main():
    # Вывод списка папок в текущей директории
    print("Доступные аккаунты:")
    account_folders = [folder for folder in os.listdir() if os.path.isdir(folder) and not folder.startswith(".")]
    for i, folder in enumerate(account_folders):
        print(f"{i+1}. {folder}")
    
    while True:
        account_choice = input("Выберите номер аккаунта: ")
        if account_choice.isdigit() and 1 <= int(account_choice) <= len(account_folders):
            account_name = account_folders[int(account_choice) - 1]
            break
        else:
             print("Некорректный выбор, попробуйте снова.")

    # Загрузка токена из файла JSON
    access_token = load_token_from_json(account_name)
    if not access_token:
        logger.error(f"Токен не найден в файле config.json для аккаунта {account_name}.")
        return

    # Авторизация
    try:
        vk = auth_vk(access_token)
    except Exception as e:
        logger.critical("Не удалось авторизоваться. Скрипт остановлен.")
        return

    # Проверка действительности токена
    if not is_token_valid(vk):
        logger.warning("Токен недействителен или истёк. Необходимо обновить токен.")
        update_token(account_name)
        # Повторная загрузка токена после обновления
        access_token = load_token_from_json(account_name)
        if not access_token:
            logger.error(f"Токен не найден в файле config.json для аккаунта {account_name}.")
            return
        # Повторная авторизация
        try:
            vk = auth_vk(access_token)
        except Exception as e:
            logger.critical("Не удалось авторизоваться. Скрипт остановлен.")
            return

    # Получаем ID текущего пользователя
    my_id = vk.users.get()[0]['id']

     # Загружаем статистику
    statistics.load_from_json()

    # Выбор действия
    while True:
        print("\nВыберите действие:")
        print("1. Поиск пользователей и сохранение их ID в файл")
        print("2. Добавление друзей из файла user_ids.txt")
        print("3. Отправка сообщений новым друзьям")
        print("4. Обработка постов друзей (лайки и комментарии)")
        print("5. Обработка постов друзей (только лайки)")
        print("6. Обработка постов друзей (только комментарии)")
        print("7. Обновить токен")
        print("8. Отправить сообщения конкретным пользователям")
        print("9. Выход")
        choice = input("Введите номер действия: ")

        if choice == "1":
            search_and_save_users(vk, account_name, statistics=statistics)
        elif choice == "2":
            add_friends_from_file(vk, account_name, statistics=statistics)
        elif choice == "3":
             send_messages_to_new_friends(vk, account_name) #не меняем статистику в send_messages_to_new_friends
        elif choice == "4":
            process_friends_posts(vk, my_id, like=True, comment=True, statistics=statistics)
        elif choice == "5":
            process_friends_posts(vk, my_id, like=True, comment=False, statistics=statistics)
        elif choice == "6":
            process_friends_posts(vk, my_id, like=False, comment=True, statistics=statistics)
        elif choice == "7":
            update_token(account_name)
        elif choice == "8":
            send_messages_to_specific_users(vk, account_name, statistics=statistics)
        elif choice == "9":
            statistics.display()
            statistics.save_to_json()
            logger.info("Завершение работы.")
            break
        else:
            logger.error("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()