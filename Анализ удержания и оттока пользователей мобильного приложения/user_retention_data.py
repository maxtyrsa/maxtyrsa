import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#Параметры для генерации данных
num_users = 1000 # Количество пользователей
start_date = datetime(2024, 1, 1) # Начальная дата установки
end_date = datetime(2024, 12, 31) # Конечная дата установки
max_sessions = 50 # Максимальное количество сессий
max_duration = 600 # Максимальная продолжительность сессии в секундах
max_actions = 100  # Максимальное количество действий
churn_rate = 0.3  # Процент ушедших пользователей

#Генерация данных
np.random.seed(42)
user_ids = np.arange(1, num_users + 1)
install_dates = [start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days)) for _ in range(num_users)]
last_session_dates = [install_date + timedelta(days=np.random.randint(0, 365)) for install_date in install_dates]
sessions_counts = np.random.randint(1, max_sessions, num_users)
session_durations = np.random.randint(10, max_duration, num_users)
actions_counts = np.random.randint(1, max_actions, num_users)
churned = np.random.choice([0, 1], num_users, p=[1 - churn_rate, churn_rate])

# Создание DataFrame
data = pd.DataFrame({
    'user_id': user_ids,
    'install_date': install_dates,
    'last_session_date': last_session_dates,
    'sessions_count': sessions_counts,
    'session_duration': session_durations,
    'actions_count': actions_counts,
    'churned': churned
})

# Пример данных
print(data.head())

# Сохранение в CSV (опционально)
data.to_csv('user_retention_data.csv', index=False)