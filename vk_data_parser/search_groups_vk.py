import requests
import json
import pandas as pd

SEARCH_QUERY = input("Запрос: ")
city_id = int(input("Идентификатор города: "))
count = int(input("Количество групп: "))

def search_vk_groups(access_token, query, group_type=None, country_id=None, city_id=None, sort=None, offset=0, count=10):

    """
     Выполняет поиск групп/сообществ ВКОНТАКТЕ на основе предоставленного запроса.
    
     Аргументы:
     access_token: Токен доступа пользователя.
     query: текст поискового запроса.
     group_type: (необязательно) Тип сообщества для поиска ("группа", "страница", "мероприятие").
     country_id: (необязательно) Идентификатор страны.
     city_id: (необязательно) Идентификатор города.
     sort: (необязательно) Тип сортировки ('0' по умолчанию, '6' для сортировки по количеству элементов)
     offset: (необязательно) Смещение для результатов.
     count: (необязательно) Количество возвращаемых результатов (не более 1000).
    
     Возвращается:
     Словарь, содержащий ответ API, или не содержащий его в случае ошибки.
     """
    
    api_url = "https://api.vk.com/method/groups.search"
    params = {
        "access_token": access_token,
        "q": query,
        "offset": offset,
        "count": count,
        "v": "5.131" # Версия API
    }
    
    if group_type:
        params["type"] = group_type
    if country_id:
        params["country_id"] = country_id
    if city_id:
      params["city_id"] = city_id
    if sort:
        params["sort"] = sort

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status() # Создать исключение для неверных кодов состояния (например, 400, 500)
        data_vk = response.json()
        return data_vk
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode json: {e}")
        return None


if __name__ == '__main__':
    # Replace with your actual access token and query
    ACCESS_TOKEN = "access_token"  
    SEARCH_QUERY = SEARCH_QUERY

    # Пример: Поиск с некоторыми необязательными параметрами
    # Москва id: 1
    
    search_data_vk = search_vk_groups(ACCESS_TOKEN, SEARCH_QUERY, group_type="group", sort='6', city_id=city_id, count=count)


    if search_data_vk and "response" in search_data_vk:
      data_vk = json.dumps(search_data_vk, indent=2, ensure_ascii=False)
    else:
      print("Something went wrong, check error messages")
json_data_vk = json.dumps(data_vk)
loaded_data_vk = json.loads(json_data_vk)
items = pd.read_json(loaded_data_vk)
count = items['response']['count']
items = items['response']['items']

# Создайте фрейм данных Pandas из этих элементов
vk = pd.DataFrame(items)
vk['count'] = count
print(vk[['screen_name', 'name']])
