import requests
import json
import pandas as pd

SEARCH_QUERY = input("Запрос: ")
city_id = int(input("Идентификатор города: "))
count = int(input("Количество групп: "))

def search_vk_groups(access_token, query, group_type=None, country_id=None, city_id=None, sort=None, offset=0, count=10):
    """
    Searches for VK groups/communities based on the provided query.

    Args:
        access_token: User access token.
        query: The search query text.
        group_type: (Optional) The type of community to search for ('group', 'page', 'event').
        country_id: (Optional) Country ID.
        city_id: (Optional) City ID.
        sort: (Optional) Sorting type ('0' for default, '6' for sorting by number of members)
        offset: (Optional) The offset for the results.
        count: (Optional) The number of results to return (max 1000).

    Returns:
        A dictionary containing the API response or None in case of an error.
    """

    api_url = "https://api.vk.com/method/groups.search"
    params = {
        "access_token": access_token,
        "q": query,
        "offset": offset,
        "count": count,
        "v": "5.131" # Specify API version
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
        response.raise_for_status() # Raise an exception for bad status codes (e.g., 400, 500)
        data = response.json()
        return data
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

    # Example: Searching with some optional parameters
    # Москва id: 1
    search_data = search_vk_groups(ACCESS_TOKEN, SEARCH_QUERY, group_type="group", sort='6', city_id=city_id, count=count)


    if search_data and "response" in search_data:
      data= json.dumps(search_data, indent=2, ensure_ascii=False)
    else:
      print("Something went wrong, check error messages")
json_data = json.dumps(data)
loaded_data = json.loads(json_data)
items = pd.read_json(loaded_data)
count = items['response']['count']
items = items['response']['items']

# Create a Pandas DataFrame from the items
df = pd.DataFrame(items)
df['count'] = count
print(df[['screen_name', 'name']])
