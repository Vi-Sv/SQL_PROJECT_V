# КЕЙС №18: СКВOЗНОЙ АНАЛИТИЧЕСКИЙ КУБ «МОСТЫ + ОКНА» И АУДИТ КОНТРАГЕНТОВ
# Реализация левостороннего объединения и параллельного оконного суммирования (PARTITION BY) через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНЫХ СТРУКТУР ФИНТЕХА
df_agents = pd.read_sql("SELECT * FROM agents", con=engine)
df_orders = pd.read_sql("SELECT * FROM agent_orders", con=engine)

# 2. РАЗВЕРТЫВАНИЕ МОСТА ДАННЫХ (Аналог LEFT JOIN)
# Объединяем справочник контрагентов с логом заказов по ключу agent_id
merged_df = pd.merge(df_agents, df_orders, on='agent_id', how='left')

# 3. КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ МЕТРИК (Data Quality)
# Нейтрализуем образовавшиеся из-за пустых связей NaN в числовые нули 0
merged_df['profit'] = merged_df['profit'].fillna(0).astype(int)

# 4. ОКOННЫЙ КОНВЕЙЕР СЕКЦИОНИРОВАНИЯ (Аналог SUM() OVER(PARTITION BY))
# Группируем объединенный массив по полю 'agent_name' без сжатия датафрейма.
# Метод .transform('sum') рассчитывает агрегат и распределяет константу по атомарным строкам
merged_df['total_agent_profit'] = merged_df.groupby('agent_name')['profit'].transform('sum')

# 5. ФОРМИРОВАНИЕ СУХОЙ АНАЛИТИЧЕСКОЙ ВИТРИНЫ
final_view = merged_df[['agent_name', 'profit', 'total_agent_profit']]
final_view.columns = ['Агенты', 'Прибыль', 'Суммарная прибыль этого агента']

# Сортируем финишный результат по алфавиту контрагентов (Аналог ORDER BY ASC)
final_view = final_view.sort_values(by='Агенты', ascending=True)
