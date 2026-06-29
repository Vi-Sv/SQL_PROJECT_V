# КЕЙС №31: СВOДНЫЕ МAТPИЦЫ И ГОРИЗОНТАЛЬНЫЙ РАЗВОРOТ PIVOT В ФИНТЕХ-КУБЕ
# Реализация поквартального горизонтального разворота (Pivot Table) через встроенные агрегаты Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНОЙ ТАБЛИЦЫ ФАКТОВ ПРОДАЖ
df = pd.read_sql("SELECT * FROM store_sales", con=engine)

# 2. ПЕРВИЧНАЯ НОРМАЛИЗАЦИЯ И КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ ИСТОЧНИКА (Data Quality)
df_clean = df.copy()
df_clean['product_line'] = df_clean['product_line'].astype(str).str.strip().str.lower()
df_clean['quarter_name'] = df_clean['quarter_name'].astype(str).str.strip() # Регистр (Q1-Q4) сохранен для консистентности
df_clean['revenue_amount'] = df_clean['revenue_amount'].fillna(0).astype(int)

# 3. РАЗВЕРТЫВАНИЕ ГОРИЗОНТАЛЬНОЙ КРОСС-МАТРИЦЫ (Аналог SUM(CASE WHEN) + GROUP BY)
# Метод .pivot_table() выполняет высокооптимизированную перегруппировку:
# index — фиксирует строки (категории), columns — разбивает на столбцы по значениям кварталов,
# values — указывает суммируемую метрику, aggfunc='sum' — выполняет агрегацию, fill_value=0 — заменяет пустые ячейки нулями.
pivot_df = df_clean.pivot_table(
    index='product_line', 
    columns='quarter_name', 
    values='revenue_amount', 
    aggfunc='sum', 
    fill_value=0
).reset_index()

# 4. СОРТИРОВКА И ПРИВЕДЕНИЕ ВИТРИНЫ К СТРОГОМУ КОРПОРАТИВНОМУ СТАНДАРТУ
# Обеспечиваем явное наличие всех 4-х кварталов в отчете, страхуя от отсутствия данных по периодам
for q in ['Q1', 'Q2', 'Q3', 'Q4']:
    if q not in pivot_df.columns:
        pivot_df[q] = 0

# Упорядочиваем столбцы и сортируем строки по алфавиту категорий продукции (Аналог ORDER BY 1 ASC)
final_view = pivot_df[['product_line', 'Q1', 'Q2', 'Q3', 'Q4']].copy()
final_view = final_view.sort_values(by='product_line', ascending=True)

# Формируем финишные алиасы витрины для коммерческого директора
final_view.columns = ['Категория продукта', 'Выручка Q1', 'Выручка Q2', 'Выручка Q3', 'Выручка Q4']
