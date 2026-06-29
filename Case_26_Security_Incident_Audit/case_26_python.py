# КЕЙС №26: КOРРEЛИРOВАННЫЕ ПОДЗАПРОСЫ И ЛOГИЧЕСКИЙ ДАТЧИК ИБ-АУДИТА
# Реализация алгоритма исключения множеств (Anti-Join / NOT EXISTS) через инструменты Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА РЕЕСТРОВ ПЕРСОНАЛА И ЛОГОВ ИНЦИДЕНТОВ
df_staff = pd.read_sql("SELECT * FROM staff_accounts", con=engine)
df_incidents = pd.read_sql("SELECT * FROM security_incidents", con=engine)

# 2. ПЕРВИЧНЫЙ ОТСЕВ И НОРМАЛИЗАЦИЯ КАЧЕСТВА ДАННЫХ (Data Quality)
# Изолируем только сотрудников целевого департамента 'Аналитика'
df_analytics = df_staff[df_staff['department'] == 'Аналитика'].copy()
df_analytics['emp_name'] = df_analytics['emp_name'].astype(str).str.strip().str.lower()

# 3. ИЗОЛЯЦИЯ МАССИВА КРИТИЧЕСКИХ НАРУШЕНИЙ ИБ
# Вычленяем из общего лога инцидентов строго уровень 'CRITICAL'
critical_incidents = df_incidents[df_incidents['severity_level'] == 'CRITICAL']

# 4. РЕАЛИЗАЦИЯ ЛОГИЧЕСКОГО ДАТЧИКА ИСКЛЮЧЕНИЯ (Аналог оператора NOT EXISTS)
# Используем метод .isin(), инвертированный оператором тильды (~).
# Это лазером вырезает из белого списка аналитиков тех, чей emp_id фигурирует в базе нарушителей
final_view = df_analytics[~df_analytics['emp_id'].isin(critical_incidents['emp_id'])].copy()

# 5. ФОРМИРОВАНИЕ СТЕРИЛЬНОЙ ИТОГОВОЙ ВИТРИНЫ БИЗНЕСА
final_view = final_view.sort_values(by='emp_name', ascending=True)
final_view = final_view[['emp_name']]
final_view.columns = ['Стерильные аналитики']
