# КЕЙС №6: РАСЧЕТ ОПЕРАЦИОННОЙ АКТИВНОСТИ КЛИЕНТСКОЙ БАЗЫ И СКВОЗНАЯ ИНТЕГРАЦИЯ ДАННЫХ
# Реализация предварительной агрегации и левостороннего сопряжения (LEFT JOIN) через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА СПРАВОЧНИКОВ И ЛОГОВ
df_users = pd.read_sql("SELECT * FROM users", con=engine)
df_orders = pd.read_sql("SELECT * FROM orders", con=engine)

# 2. ВАЛИДАЦИЯ ИСХОДНЫХ МЕТРИК В ТАБЛИЦЕ ЗАКАЗОВ
df_orders['payment_amount'] = df_orders['payment_amount'].fillna(0).astype(int)

# 3. ПРЕДВАРИТЕЛЬНАЯ АГРЕГАЦИЯ ДАННЫХ (Аналог подзапроса во FROM)
# Схлопываем многократные дубли транзакций по каждому user_id до объединения таблиц
orders_agg = df_orders.groupby('user_id')['payment_amount'].sum().reset_index()
orders_agg.columns = ['user_id', 'total_payment']

# 4. РАЗВЕРТЫВАНИЕ МОСТА ДАННЫХ (Аналог LEFT JOIN)
# Параметр how='left' оставляет справочник клиентов неприкасаемым и сохраняет "молчунов"
merged_df = pd.merge(df_users, orders_agg, on='user_id', how='left')

# 5. ФИНАЛЬНАЯ ЗАЧИСТКА ПУСТОТ И ФОРМИРОВАНИЕ ВИТРИНЫ
# Заменяем образовавшиеся из-за пустых связей NULL (NaN) на жесткие нули
merged_df['total_payment'] = merged_df['total_payment'].fillna(0).astype(int)

# Выделяем целевые колонки для руководства
final_view = merged_df[['user_id', 'phone', 'total_payment']]
final_view.columns = ['ID пользователя', 'Номер телефона', 'Сумма покупок']
