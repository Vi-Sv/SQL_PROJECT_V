# КЕЙС №15: ЮВЕЛИРНОЕ РАНЖИРОВАНИЕ ДАТА-КАНДИДАТОВ И ОКОННЫЙ СРЕЗ РЕЙТИНГА МЕСТ
# Реализация плотного аналитического ранжирования (DENSE_RANK) и фильтрации Top-N через Pandas

import pandas as pd

# 1. ВХОДНОЙ КОНВЕЙЕР И ЗАГРУЗКА РЕЗУЛЬТАТОВ КОНКУРСА
df = pd.read_sql("SELECT * FROM contest_scores", con=engine)

# 2. ТЕКСТОВАЯ НОРМАЛИЗАЦИЯ И КАЧЕСТВЕННАЯ ВАЛИДАЦИЯ ДАННЫХ (Data Quality)
df['candidate_name'] = df['candidate_name'].astype(str).str.strip().str.lower()
df['score'] = df['score'].fillna(0).astype(int)

# 3. ХРОНОЛОГИЧЕСКАЯ СОРТИРОВКА ПЕРЕД ВЫЧИСЛЕНИЕМ ПЛОТНОГО РАНГА
# Упорядочиваем датафрейм по ID департаментов (возрастание) и баллам (убывание)
df = df.sort_values(by=['department_id', 'score'], ascending=[True, False]).copy()

# 4. ОКОННЫЙ КОНВЕЙЕР ПЛОТНОГО РАНЖИРОВАНИЯ (Аналог DENSE_RANK() OVER(PARTITION BY ... ORDER BY DESC))
# Группируем фрейм по department_id для изоляции конкурсных цехов.
# Метод .rank(method='dense', ascending=False) присваивает плотные ранги без математических дыр и прыжков
df['dense_rank_place'] = df.groupby('department_id')['score'].rank(method='dense', ascending=False).astype(int)

# 5. ХИРУРГИЧЕСКИЙ ОТСЕВ ПОДВИЖНЫХ АГРЕГАТОВ (Аналог WHERE g4 <= 2)
# Срезаем конкурсный мусор, оставляя на экране строго 1-е и 2-е призовые места в каждом департаменте
final_view = df[df['dense_rank_place'] <= 2].copy()

# 6. СОРТИРОВКА И ФОРМИРОВАНИЕ ФИНАЛЬНОЙ ВИТРИНЫ
final_view = final_view.sort_values(by=['department_id', 'score'], ascending=[True, False])
final_view = final_view[['department_id', 'candidate_name', 'score', 'dense_rank_place']]
final_view.columns = ['Номера департаментов', 'Чистые имена', 'Баллы', 'Рейтинг мест']
