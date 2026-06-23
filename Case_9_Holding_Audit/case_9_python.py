# КЕЙС №9: СКВОЗНОЙ ТРОЙНОЙ МОСТ И МНОГОМЕРНЫЙ ФИНАНСОВЫЙ АУДИТ ХОЛДИНГА
# Реализация многоэтапного последовательного левостороннего объединения и предварительной агрегации через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА СПРАВОЧНИКОВ И РЕЕСТРОВ ХОЛДИНГА
df_agents = pd.read_sql("SELECT * FROM agents", con=engine)
df_contracts = pd.read_sql("SELECT * FROM contracts", con=engine)
df_payments = pd.read_sql("SELECT * FROM payments", con=engine)

# 2. ПРЕДВАРИТЕЛЬНАЯ АГРЕГАЦИЯ И ВАЛИДАЦИЯ ТРАНЗАКЦИОННОГО МАССИВА (Аналог подзапроса t3)
# Нейтрализуем пропуски NULL (NaN) в суммах до этапа математического суммирования
df_payments['amount'] = df_payments['amount'].fillna(0).astype(int)

# Сжимаем транзакционный лог до уникальных ключей договоров, устраняя дублирование платежей
payments_agg = df_payments.groupby('contract_id')['amount'].sum().reset_index()
payments_agg.columns = ['contract_id', 'total_amount']

# 3. НОРМАЛИЗАЦИЯ ТЕКСТОВЫХ ПОЛЕЙ В СПРАВОЧНИКАХ
df_agents['agent_name'] = df_agents['agent_name'].astype(str).str.strip().str.lower()
df_contracts['contract_type'] = df_contracts['contract_type'].astype(str).str.strip().str.lower()

# 4. РАЗВЕРТЫВАНИЕ ПОСЛЕДОВАТЕЛЬНОГО МНОГОМЕРНОГО МОСТА (Аналог цепочки LEFT JOIN)
# Шаг А: Пришиваем к справочнику агентов таблицу спецификации договоров
merged_first = pd.merge(df_agents, df_contracts, on='agent_id', how='left')

# Шаг Б: Пришиваем сжатый агрегированный массив платежей по ключу contract_id
final_merged = pd.merge(merged_first, payments_agg, on='contract_id', how='left')

# 5. ФИНАЛЬНАЯ ЗАЧИСТКА ВНЕШНИХ ПУСТОТ И ФОРМИРОВАНИЕ ВИТРИНЫ
# Намертво преобразуем образовавшиеся из-за пустых связей NaN в жесткие нули
final_merged['total_amount'] = final_merged['total_amount'].fillna(0).astype(int)

# Замена системных пустых строк в типах договоров на маркер отсутствия контракта
final_merged['contract_type'] = final_merged['contract_type'].fillna('нет договора')

# Выделяем целевые аналитические столбцы для генерального директора
final_view = final_merged[['agent_name', 'contract_type', 'total_amount']]
final_view.columns = ['Имена контрагентов', 'Тип их договоров', 'Общая сумма платежей']
