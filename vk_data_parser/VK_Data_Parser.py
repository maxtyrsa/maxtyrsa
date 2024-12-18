import requests
import json
import time
from datetime import datetime
import os

def load_config(config_file="/storage/emulated/0/Documents/api/config.json"):
    """Загружает конфигурацию из JSON-файла"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: {config_file} not found. Please add your token there.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {config_file} is not a valid JSON file.")
        return None

def get_vk_members(group_id, token, offset=0, count=1000):
    """Получает список id пользователей группы."""
    url = "https://api.vk.com/method/groups.getMembers"
    params = {
        "group_id": group_id,
        "v": 5.131,
        "access_token": token,
        "offset": offset,
        "count": count,
        "fields": "sex, bdate, city"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверить статус ответа
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None

def get_user_info(user_id, token):
    """Получает информацию о пользователе."""
    url = "https://api.vk.com/method/users.get"
    params = {
        "user_ids": user_id,
        "v": 5.131,
        "access_token": token,
        "fields": "sex, bdate, city"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Проверить статус ответа
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None

def filter_users(users, min_age, max_age, sex, city=None):
    """Фильтрует пользователей по возрасту, полу и городу."""
    filtered_users = []
    for user in users:
        if 'bdate' in user:
            try:
              bdate = user['bdate']
              birthdate = datetime.strptime(bdate, "%d.%m.%Y")
              age = datetime.now().year - birthdate.year
            except:
              try:
                 bdate = user['bdate']
                 birthdate = datetime.strptime(bdate, "%d.%m")
                 age = datetime.now().year - birthdate.year
              except:
                 continue

            if min_age <= age <= max_age:
                if sex == 1 and user.get("sex") == 1:
                    if city:
                      if 'city' in user and user['city'].get('title') == city:
                         filtered_users.append(user)
                      elif not city:
                        filtered_users.append(user)
                    else:
                      filtered_users.append(user)
                elif sex == 2 and user.get("sex") == 2:
                    if city:
                        if 'city' in user and user['city'].get('title') == city:
                          filtered_users.append(user)
                        elif not city:
                          filtered_users.append(user)
                    else:
                       filtered_users.append(user)
        elif 'city' in user:
            if sex == 1 and user.get("sex") == 1:
              if city:
                  if user['city'].get('title') == city:
                      filtered_users.append(user)
              else:
                filtered_users.append(user)
            elif sex == 2 and user.get("sex") == 2:
                if city:
                  if user['city'].get('title') == city:
                      filtered_users.append(user)
                else:
                  filtered_users.append(user)

    return filtered_users

def save_users_to_file(users, filename="filtered_users.json"):
    """Сохраняет список пользователей в файл JSON."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        print(f"Данные сохранены в файл: {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

if __name__ == "__main__":
    config = load_config()
    if not config or 'vk_token' not in config:
        print("Ошибка загрузки токена. Выход.")
        exit()

    token_vk = config['vk_token']
    print(f"Loaded Token: {token_vk}") # Выводим токен для проверки

    group_ids_input = input('Введите id групп через запятую (например, krdbaraholka,public123): ')
    group_ids = [group.strip() for group in group_ids_input.split(',')]
    start_age = int(input('Age min: '))
    end_age = int(input('Age max: '))
    sex = int(input('Sex (1 - женщины, 2 - мужчины): '))
    city = input('Введите город (или нажмите Enter, чтобы пропустить фильтрацию по городу): ') or None

    all_members = []

    for group_id in group_ids:
        offset = 0
        count = 1000
        print(f"Сбор пользователей из группы: {group_id}")
        while True:
            result = get_vk_members(group_id, token_vk, offset=offset, count=count)
            if not result or 'response' not in result or not result['response']['items']:
                break
            all_members.extend(result['response']['items'])
            offset += count
            time.sleep(0.5)

    filtered_users = filter_users(all_members, start_age, end_age, sex, city)
    print("Количество отфильтрованных пользователей:", len(filtered_users))
    save_users_to_file(filtered_users)