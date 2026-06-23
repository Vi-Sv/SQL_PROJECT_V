# КЕЙС №16: МАТЕМАТИЧЕСКОЕ СГЛАЖИВАНИЕ ТРЕНДОВ И СKОЛЬЗЯЩЕЕ СРЕДНЕЕ В РИТЕЙЛЕ
# Реализация трехдневного скользящего среднего на календарных интервалах времени через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА ИСХОДНОГО МАССИВА ДАННЫХ
df = pd.read_sql("SELECT * FROM daily_shop_revenue", con=engine)

# 2. ВАЛИДАЦИЯ ФИНАНСОВЫХ МЕТРИК И ПРИВЕДЕНИЕ ТИПОВ ВРЕМЕННОГО РЯДА
df['daily_revenue'] = df['daily_revenue'].fillna(0).astype(int)
df['report_date'] = pd.to_datetime(df['report_date'])

# 3. ПРЕДВАРИТЕЛЬНАЯ ЖЕСТКАЯ СОРТИРОВКА (Обязательный шаг перед скользящими окнами)
df = df.sort_values(by=['shop_id', 'report_date'], ascending=[True, True]).copy()

# 4. КАЛЕНДАРНОЕ СKОЛЬЗЯЩЕЕ ОКНО (Зеркало сеньорского RANGE BETWEEN INTERVAL)
# Для работы скользящего окна по временным зазорам (а не строкам) временно устанавливаем индекс на report_date.
# Конструкция .groupby('shop_id') изолирует торговые точки.
# Инструмент .rolling('3D', closed='right') разворачивает ползающий лифт времени на 3 календарных суток назад.
# Вычисляем среднее .mean() и возвращаем индекс в исходное состояние.
df['rolling_average_3d'] = (
    df.set_index('report_date')
    .groupby('shop_id')['daily_revenue']
    .rolling('3D', closed='right')
    .mean()
    .round(2)
    .values
)

# 5. ФОРМИРОВАНИЕ И ОФОРМЛЕНИЕ ФИНАЛЬНОЙ ВИТРИНЫ ДЛЯ ИНВЕСТОРОВ
final_view = df[['shop_id', 'report_date', 'daily_revenue', 'rolling_average_3d']]
final_view.columns = ['Номера магазинов', 'Дата торговых дней', 'Чистая выручка', 'Скользящее среднее (3 дня)']
