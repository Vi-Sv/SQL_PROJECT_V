# КЕЙС №17: ОКОННЫЕ ФИЛЬТРЫ И ИЗОЛЯЦИЯ АБСОЛЮТНЫХ ЛИДЕРОВ КАТЕГОРИЙ В РИТЕЙЛЕ
# Реализация аналитического ранжирования (ROW_NUMBER) и фильтрации абсолютных лидеров (Top-1) через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА РЕЕСТРА ПРОДАЖ АГЕНТОВ
df = pd.read_sql("SELECT * FROM agent_sales", con=engine)

# 2. ТЕКСТОВАЯ НОРМАЛИЗАЦИЯ И ВАЛИДАЦИЯ ИСХОДНЫХ МЕТРИК (Data Quality)
# Удаляем концевые пробелы и приводим текстовые поля контрагентов и категорий к нижнему регистру
df['agent_name'] = df['agent_name'].astype(str).str.strip().str.lower()
df['category'] = df['category'].astype(str).str.strip().str.lower()

# Заменяем системные пустоты NULL в прибыли чистыми числовыми нулями
df['profit'] = df['profit'].fillna(0).astype(int)

# 3. ЖЕСТКАЯ ПРЕДВАРИТЕЛЬНАЯ СОРТИРОВКА ПОТОКА ДАННЫХ
# Упорядочиваем датафрейм по категориям (возрастание) и объемам прибыли (убывание)
df = df.sort_values(by=['category', 'profit'], ascending=[True, False]).copy()

# 4. ОКОННЫЙ КОНВЕЙЕР РАНЖИРОВАНИЯ (Аналог ROW_NUMBER() OVER(PARTITION BY ... ORDER BY DESC))
# Группируем фрейм по нормализованному полю 'category' для локализации вычислений.
# Счетчик .cumcount() присваивает сквозные индексы строкам внутри группы от 0 (прибавляем 1 для соответствия SQL-рангам)
df['row_rank'] = df.groupby('category').cumcount() + 1

# 5. ХИРУРГИЧЕСКАЯ ФИЛЬТРАЦИЯ СКАЛЬПЕЛЕМ TOP-1 (Аналог WHERE t2.g4 = 1)
# Вырезаем по одному абсолютному чемпиону на каждую категорию ритейла
final_view = df[df['row_rank'] == 1].copy()

# 6. ФОРМИРОВАНИЕ СТЕРИЛЬНОЙ ВИТРИНЫ ДЛЯ ИНВЕСТОРОВ И МЕНЕДЖМЕНТА
final_view = final_view[['agent_name', 'category', 'profit', 'row_rank']]
final_view.columns = ['Агенты', 'Категория', 'Прибыль', 'Топ_1']
final_view = final_view.sort_values(by='Категория', ascending=True)
