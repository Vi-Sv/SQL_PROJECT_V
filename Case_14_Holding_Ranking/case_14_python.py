# КЕЙС №14: ОКОННОЕ РАНЖИРОВАНИЕ ROW_NUMBER И ВЫРЕЗАНИЕ ТОП-3 КРУПНЫХ ПЛАТЕЖЕЙ
# Реализация аналитического ранжирования (ROW_NUMBER) и фильтрации Top-N через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА РЕГИОНАЛЬНЫХ ТРАНЗАКЦИЙ
df = pd.read_sql("SELECT * FROM regional_payments", con=engine)

# 2. ТЕКСТОВАЯ НОРМАЛИЗАЦИЯ И ВАЛИДАЦИЯ ИСХОДНЫХ МЕТРИК
df['region_name'] = df['region_name'].astype(str).str.strip().str.lower()
df['pay_amount'] = df['pay_amount'].fillna(0).astype(int)

# 3. СОРТИРОВКА ПОТОКА ПЕРЕД ВЫЧИСЛЕНИЕМ РАНГОВ (Критически важный шаг)
# Сортируем фрейм по регионам (возрастание) и суммам платежей (убывание)
df = df.sort_values(by=['region_name', 'pay_amount'], ascending=[True, False]).copy()

# 4. ОКОННЫЙ КОНВЕЙЕР РАНЖИРОВАНИЯ (Аналог ROW_NUMBER() OVER(PARTITION BY ... ORDER BY DESC))
# Группируем датафрейм по регионам через .groupby('region_name')
# Инструмент .cumcount() запускает внутренний счетчик строк внутри группы, начиная с 0 (прибавляем 1 для рангов от 1)
df['row_rank'] = df.groupby('region_name').cumcount() + 1

# 5. ХИРУРГИЧЕСКИЙ ОТСЕВ TOP-N (Аналог WHERE IN (1,2,3))
# Оставляем в датафрейме только строки, чей ранг входит в топ-3
final_view = df[df['row_rank'].isin([1, 2, 3])].copy()

# 6. ФОРМИРОВАНИЕ ФИНАЛЬНОЙ СТРУКТУРИРОВАННОЙ ВИТРИНЫ
final_view = final_view[['region_name', 'client_id', 'pay_amount', 'row_rank']]
final_view.columns = ['Регионы', 'ID клиента', 'Сумма платежа', 'Рейтинг']
