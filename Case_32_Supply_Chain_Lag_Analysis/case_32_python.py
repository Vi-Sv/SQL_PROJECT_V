# КЕЙС №32: ОКOННЫЙ ЛAГ-АНАЛИЗ И ХРOНOЛОГИЧЕСКИЙ ШПИОНАЖ LAG В ЛОГИСТИКЕ ПТО
# Реализация аналитического смещения строк назад (LAG) во временных рядах через инструменты Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНОГО МАССИВА ЛОГИСТИКИ СНАБЖЕНИЯ
df = pd.read_sql("SELECT * FROM supply_orders", con=engine)

# 2. ПРИВЕДЕНИЕ ТИПОВ ДАННЫХ И КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ (Data Quality)
df_clean = df.copy()
df_clean['delivery_date'] = pd.to_datetime(df_clean['delivery_date'])
df_clean['delay_days'] = df_clean['delay_days'].fillna(0).astype(int)

# 3. ЖЕСТКАЯ ХРОНОЛОГИЧЕСКАЯ СОРТИРОВКА ПОТОКА (Обязательный шаг перед вызовом .shift())
# Упорядочиваем датафрейм по ID поставщиков и возрастанию дат отгрузок
df_clean = df_clean.sort_values(by=['supplier_id', 'delivery_date'], ascending=[True, True]).copy()

# 4. ОКOННЫЙ КОНВЕЙЕР СМЕЩЕНИЯ НАЗАД (Аналог LAG() OVER(PARTITION BY ... ORDER BY))
# Группируем массив по 'supplier_id' для изоляции истории логистики каждого контрагента.
# Инструмент .shift(1) выполняет контролируемое смещение вектора данных на одну строку вниз (шаг назад во времени).
# Заменяем образовавшиеся на границах групп NaN на жесткие нули 0.
df_clean['prev_delay'] = df_clean.groupby('supplier_id')['delay_days'].shift(1).fillna(0).astype(int)

# 5. ФОРМИРОВАНИЕ И ОФОРМЛЕНИЕ ФИНАЛЬНОЙ СТРУКТУРИРОВАННОЙ ВИТРИНЫ
final_view = df_clean[['order_id', 'delay_days', 'prev_delay']]
final_view.columns = ['Заказы', 'Текущее опоздание', 'Задержка предыдущего заказа']

# Финальное выравнивание витрины (Аналог глобального ORDER BY)
final_view = final_view.sort_values(by=list(df_clean[['supplier_id', 'order_id']].columns))
