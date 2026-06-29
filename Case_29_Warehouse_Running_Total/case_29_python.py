# КЕЙС №29: ОКОННЫЕ РАЗВИЛКИ CASE WHEN И НАКОПИТЕЛЬНЫЙ ИТОГ ОПЕРАЦИОННОГО БАЛАНСА СКЛАДА
# Реализация условного нарастающего итога (Conditional Running Total) временного ряда через Pandas

import pandas as pd
import numpy as np

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНЫХ ЛОГОВ СКЛАДСКОГО УЧЕТА
df = pd.read_sql("SELECT * FROM warehouse_logs", con=engine)

# 2. ПЕРВИЧНАЯ НОРМАЛИЗАЦИЯ И КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ ИСТОЧНИКА (Data Quality)
df_clean = df.copy()
df_clean['operator_name'] = df_clean['operator_name'].astype(str).str.strip().str.lower()
df_clean['quantity'] = df_clean['quantity'].fillna(0).astype(int)

# 3. ЖЕСТКАЯ ХРОНОЛОГИЧЕСКАЯ СОРТИРОВКА ПОТОКА (Критически важный шаг)
# Сортируем датафрейм по операторам и возрастанию уникальных ID логов
df_clean = df_clean.sort_values(by=['operator_name', 'log_id'], ascending=[True, True]).copy()

# 4. ВНЕДРЕНИЕ ЗНАКОВОГО ПЕРЕКЛЮЧАТЕЛЯ (Аналог условного CASE WHEN внутри SUM)
# С помощью np.select инвертируем знаки объемов: приход в плюс, возврат в жесткий минус
conditions = [
    df_clean['operation_type'] == 'ПРИХОД',
    df_clean['operation_type'] == 'ВОЗВРАТ'
]
choices = [
    df_clean['quantity'],
    -df_clean['quantity']
]
df_clean['signed_quantity'] = np.select(conditions, choices, default=0)

# 5. ОКОННЫЙ СКОЛЬЗЯЩИЙ ПОДCЧЕТ НАРАСТАЮЩЕГО ИТОГА (Аналог SUM() OVER(PARTITION BY ... ROWS))
# Группируем массив по 'operator_name' без сжатия строк датафрейма.
# Метод .cumsum() выполняет последовательное кумулятивное сложение элементов сверху вниз внутри группы
df_clean['running_warehouse_balance'] = df_clean.groupby('operator_name')['signed_quantity'].cumsum()

# 6. ФОРМИРОВАНИЕ СТЕРИЛЬНОЙ ФИНАЛЬНОЙ ВИТРИНЫ
final_view = df_clean[['log_id', 'operator_name', 'running_warehouse_balance']]
final_view.columns = ['ID', 'g1', 'Накопительный баланс склада']
final_view = final_view.sort_values(by=['g1', 'ID'], ascending=[True, True])
