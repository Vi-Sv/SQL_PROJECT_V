# КЕЙС №22: СТE-АГРЕГАЦИЯ И СКВOЗНОЙ АНАЛИТИЧЕСКИЙ МОСТ В КАДРОВОМ АУДИТЕ
# Реализация предварительной агрегации, внутреннего сопряжения (INNER JOIN) и фильтрации отклонений через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНЫХ ДАННЫХ ШТАТНОГО РАСПИСАНИЯ
df = pd.read_sql("SELECT * FROM employee_salaries", con=engine)

# 2. КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ И ТЕКСТОВАЯ НОРМАЛИЗАЦИЯ ИСТОЧНИКА (Data Quality)
df_clean = df.copy()
df_clean['department_name'] = df_clean['department_name'].astype(str).str.strip().str.lower()
df_clean['salary'] = df_clean['salary'].fillna(0).astype(int)

# 3. ВЫЧИСЛИТЕЛЬНЫЙ ЦЕХ АГРЕГАЦИИ (Аналог конструкции WITH dept_averages AS)
# Сжимаем данные на нижнем уровне до уникальных департаментов и рассчитываем среднее арифметическое
dept_avg = df_clean.groupby('department_name')['salary'].mean().round(2).reset_index()
dept_avg.columns = ['department_name', 'avg_salary']

# 4. РАЗВЕРТЫВАНИЕ МОСТА ДАННЫХ «ОДИН КО МНОГИМ» (Аналог INNER JOIN)
# Сопрягаем детальный лог сотрудников со сжатой матрицей средних окладов по ключу департамента
merged_df = pd.merge(df_clean, dept_avg, on='department_name', how='inner')

# 5. ХИРУРГИЧЕСКОЕ СИТО ФИЛЬТРАЦИИ ОТКЛОНЕНИЙ (Аналог WHERE salary > avg_salary)
# Вырезаем сотрудников, чей личный оклад строго превышает средний норматив подразделения
final_view = merged_df[merged_df['salary'] > merged_df['avg_salary']].copy()

# 6. СОРТИРОВКА И ФОРМИРОВАНИЕ ФИНАЛЬНОЙ СТРУКТУРИРОВАННОЙ ВИТРИНЫ
final_view = final_view.sort_values(by='salary', ascending=False)
final_view = final_view[['emp_id', 'department_name', 'salary', 'avg_salary']]
final_view.columns = ['ID сотрудника', 'Департамент', 'Оклад', 'Средний оклад по департаменту']
