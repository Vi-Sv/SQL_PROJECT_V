# КЕЙС №20: МНОГОСТУПЕНЧАТЫЕ CTE-МАГИСТРАЛИ И СЕКЦИОНИРОВАНИЕ ТОП-2 ПЕРЕВОДОВ ХОЛДИНГА
# Реализация обобщенных табличных выражений (CTE) и оконного секционирования Top-N через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНОГО МАССИВА МЕЖБАНКОВСКИХ ПЕРЕВОДОВ
df = pd.read_sql("SELECT * FROM branch_transfers", con=engine)

# 2. ИЗОЛИРОВАННЫЙ ЦЕХ ОЧИСТКИ И СЕКЦИОНИРОВАНИЯ (Аналог конструкции WITH cleansed_branches AS)
clean_df = df.copy()

# Нормализуем географические коды: удаляем пробелы и приводим к нижнему регистру (Data Quality)
clean_df['branch_code'] = clean_df['branch_code'].astype(str).str.strip().str.lower()

# Валидируем финансовую метрику: нейтрализуем пропуски NULL (NaN) жесткими нулями 0
clean_df['transfer_amount'] = clean_df['transfer_amount'].fillna(0).astype(int)

# Хронологическая предварительная сортировка потока внутри групп перед расчетом рангов
clean_df = clean_df.sort_values(by=['branch_code', 'transfer_amount'], ascending=[True, False]).copy()

# Запускаем оконный автоматический нумератор (Аналог ROW_NUMBER() OVER(PARTITION BY ... ORDER BY DESC))
# Счетчик .cumcount() присваивает сквозные индексы строкам внутри каждого города, начиная с 0 (+1 для SQL-стандарта)
clean_df['row_rank'] = clean_df.groupby('branch_code').cumcount() + 1

# 3. ГЛАВНЫЙ КОНТУР ФИЛЬТРАЦИИ И ВЫВОД НА СТЕРИЛЬНУЮ ВИТРИНУ
# Оставляем только те строки, чей локальный ранг попал в рамки ТОП-2 (Аналог WHERE g3 <= 2)
final_view = clean_df[clean_df['row_rank'] <= 2].copy()

# Сортируем итоговый VIP-отчет по алфавиту городов и возрастанию рангов мест от 1 до 2
final_view = final_view.sort_values(by=['branch_code', 'row_rank'], ascending=[True, True])

# Выделяем целевые аналитические колонки отчета для руководства холдинга
final_view = final_view[['branch_code', 'transfer_amount', 'row_rank']]
final_view.columns = ['Города', 'Сумма', 'Ранг']
