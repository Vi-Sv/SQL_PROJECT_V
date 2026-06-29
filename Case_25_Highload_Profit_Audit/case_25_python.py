# КЕЙС №25: ТРEХЭТАЖНЫЕ CTE-МАГИСТРАЛИ И VIP-АУДИТ ПРИБЫЛИ ХОЛДИНГА
# Реализация каскадных вычислительных магистралей (последовательных CTE) и фильтрации Top-N через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНЫХ КОММЕРЧЕСКИХ ЛОГОВ ПРОДАЖ
df = pd.read_sql("SELECT * FROM sales_deals", con=engine)

# 2. ПЕРВЫЙ ЭТАП ОБРАБОТКИ — ЦЕХ ОЧИСТКИ (Аналог конструкции WITH raw_cleansing AS)
# Выполняем базовые процедуры Data Quality на изолированном датафрейме
clean_df = df.copy()

# Нормализуем имена контрагентов: удаляем концевые пробелы и приводим к нижнему регистру
clean_df['client_name'] = clean_df['client_name'].astype(str).str.strip().str.lower()

# Нейтрализуем системные пропуски NULL в финансовых метриках выручки и налогов жесткими нулями 0
clean_df['gross_revenue'] = clean_df['gross_revenue'].fillna(0).astype(int)
clean_df['tax_deduction'] = clean_df['tax_deduction'].fillna(0).astype(int)

# Выделяем столбцы и сопоставляем их с алиасами первого цеха
clean_df = clean_df[['client_name', 'gross_revenue', 'tax_deduction']]
clean_df.columns = ['g1', 'g2', 'g3']

# 3. ВТOРОЙ ЭТАП ОБРАБОТКИ — РАСЧЕТ ПРОФИТА (Аналог каскада profit_calculation AS)
# Перехватываем очищенный массив данных из предыдущего этапа clean_df
profit_df = clean_df.copy()

# На лету рассчитываем чистую прибыль как разницу между валовым доходом и налогами
profit_df['f2'] = profit_df['g2'] - profit_df['g3']
profit_df = profit_df.rename(columns={'g1': 'f1'})

# 4. ГЛАВНЫЙ ВНЕШНИЙ КОНТУР И ИЗОЛЯЦИЯ VIP-ПРОФИТА СВЫШЕ ПОРОГА (Аналог WHERE > 500000)
# Применяем сито строгого неравенства и отсекаем технические записи по маске строки
final_view = profit_df[
    (profit_df['f2'] > 500000) & 
    (~profit_df['f1'].str.contains('тест', na=False))
].copy()

# Формируем и упорядочиваем финишную витрину по убыванию маржинальности (Аналог ORDER BY DESC)
final_view = final_view.sort_values(by='f2', ascending=False)
final_view = final_view[['f1', 'f2']]
final_view.columns = ['Имя клиента', 'Чистая прибыль']
