# КЕЙС №12: АНАЛИЗ РИТМИЧНОСТИ ПОСТАВОК И ПРОЕКТИРОВАНИЕ ГРАФИКА ЗАЗОРОВ СНАБЖЕНИЯ
# Реализация аналитического смещения вперед (LEAD) в логистических секциях через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ЛОГИСТИЧЕСКИХ ДАННЫХ ПТО
df = pd.read_sql("SELECT * FROM materials_delivery", con=engine)

# 2. ТЕКСТОВАЯ НОРМАЛИЗАЦИЯ И СТАНДАРТИЗАЦИЯ НОМЕНКЛАТУРЫ
df['material_name'] = df['material_name'].astype(str).str.strip().str.lower()

# 3. ВАЛИДАЦИЯ И ПРИВЕДЕНИЕ ТИПОВ ВРЕМЕННОГО РЯДА
df['delivery_date'] = pd.to_datetime(df['delivery_date'])

# 4. ХРОНОЛОГИЧЕСКАЯ СОРТИРОВКА ПОТОКА ПЕРЕД СМЕЩЕНИЕМ
df = df.sort_values(by=['material_name', 'delivery_date'], ascending=[True, True]).copy()

# 5. ОКОННЫЙ КОНВЕЙЕР СМЕЩЕНИЯ ВПЕРЕД (Аналог LEAD() OVER(PARTITION BY ... ORDER BY))
# Группируем фрейм по clean_material_name для изоляции вычислений.
# Метод .shift(-1) выполняет сдвиг вектора данных на одну строку вверх (шаг вперед в будущее).
# Финальная строка группы автоматически принимает значение NaT (системный NULL для дат), сохраняя тип данных.
df['next_delivery_date'] = df.groupby('material_name')['delivery_date'].shift(-1)

# 6. ФОРМИРОВАНИЕ ФИНАЛЬНОЙ СТРУКТУРИРОВАННОЙ ВИТРИНЫ
final_view = df[['material_name', 'delivery_date', 'tonnage', 'next_delivery_date']]
final_view.columns = ['Название материала', 'Дата текущей поставки', 'Объем (тонн)', 'Дата следующей поставки']
