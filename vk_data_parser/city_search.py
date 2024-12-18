import requests

def get_cities(access_token, region_id=None, q=None, need_all=0, offset=0, count=100):
    """
    Получает список городов через API VK.

    Args:
      access_token: Токен доступа VK.
      region_id: Идентификатор региона (необязательный).
      q: Строка поиска (необязательный).
      need_all: Флаг, возвращать все города или только основные (0 или 1).
      offset: Отступ для постраничной навигации (необязательный).
      count: Количество городов для возврата.

    Returns:
      Словарь с данными о городах или None в случае ошибки.
    """
    url = 'https://api.vk.com/method/database.getCities'
    params = {
        'access_token': access_token,
        'v': '5.199',
        'need_all': need_all,
        'offset': offset,
        'count': count
    }
    
    if region_id:
        params['region_id'] = region_id
    
    if q:
        params['q'] = q

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('response')
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при запросе к API VK: {e}')
        return None


def main():
    access_token = 'access_token'  # Замените на свой токен

    while True:
       city_name = input("Введите название города (или 'выход' для завершения): ")
       if city_name.lower() == 'выход':
           break

       cities = get_cities(access_token, q=city_name, count=10)

       if cities and cities.get('items'):
           print(f"\nРезультаты поиска для '{city_name}':")
           for city in cities['items']:
               print(f"ID: {city.get('id')}, Название: {city.get('title')}")
           print(f"Всего городов: {cities.get('count')}")

       elif cities:
           print(f"Нет городов, соответствующих '{city_name}'.")

       else:
         print("Не удалось получить результаты поиска.")

if __name__ == '__main__':
    main()
