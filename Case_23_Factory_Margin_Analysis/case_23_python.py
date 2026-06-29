# КЕЙС №23: ТРEХЭТАЖНЫЕ КAСКАДНЫЕ СТЕ-МАГИСТРАЛИ И АНАЛИЗ РЕНТАБЕЛЬНОСТИ ПРОИЗВОДСТВА
# Реализация многоэтапного куба вычислений и каскадной фильтрации маржи через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ПРОИЗВОДСТВЕННЫХ ЛОГОВ ЗАВОДА
df = pd.read_sql("SELECT * FROM product_manufacturing", con=engine)

# 2. ПЕРВЫЙ ЭТАП ОБРАБОТКИ — ЦЕХ ОЧИСТКИ (Аналог конструкции WITH base_cleansing AS)
# Проводим базовые процедуры Data Quality на изолированном датафрейме
base_df = df.copy()

# Нормализуем наименования производственных площадок
base_df['factory_name'] = base_df['factory_name'].astype(str).str.strip().str.lower()

# Нейтрализуем системные пустоты NULL в финансовых метриках розницы и себестоимости
base_df['production_cost'] = base_df['production_cost'].fillna(0).astype(int)
base_df['market_price'] = base_df['market_price'].fillna(0).astype(int)

# Переименовываем столбцы под внутренний технический стандарт первого цеха
base_df = base_df[['factory_name', 'production_cost', 'market_price']]
base_df.columns = ['g1', 'g2', 'g3']

# 3. ВТOРОЙ ЭТАП ОБРАБОТКИ — ВЫЧИСЛЕНИЕ ДЕЛЬТЫ (Аналог каскада margin_calc AS)
# Строго перехватываем чистый массив данных из предыдущего этапа base_df
margin_df = base_df.copy()

# На лету рассчитываем маржинальность как разницу между розничной ценой и затратами
margin_df['f3'] = margin_df['g3'] - margin_df['g2']
margin_df = margin_df.rename(columns={'g1': 'f1', 'g2': 'f2'})

# 4. ГЛАВНЫЙ ВНЕШНИЙ КОНТУР И ИЗОЛЯЦИЯ СКРЫТЫХ УБЫТКОВ (Аналог WHERE f3 <= 0)
# [Исправление] Фильтрация и вывод переведены на целевую маржинальную дельту 'f3' (не себестоимость)
final_view = margin_df[
    (margin_df['f3'] <= 0) & 
    (~margin_df['f1'].str.contains('тест', na=False))
].copy()

# Формируем и упорядочиваем финишную витрину по убыванию маржи (Аналог ORDER BY DESC)
final_view = final_view.sort_values(by='f3', ascending=False)
final_view = final_view[['f1', 'f3']]
final_view.columns = ['Завод-изготовитель', 'Маржа']
