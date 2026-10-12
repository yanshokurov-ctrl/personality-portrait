# API ядра модуля

Ядро модуля — это движок опроса (`app/engine/session.py`), сборщик результатов
(`app/collector/collector.py`) и список методик (`app/methodologies/registry.py`).
Структуры данных описаны в [architecture.md](architecture.md#контракт-методики).

## Быстрый пример

```python
from app.engine.session import SurveySession
from app.methodologies.registry import get_methodologies

session = SurveySession(get_methodologies())
while not session.is_finished():
    question = session.current_question()
    session.answer(question.options[0].value)
    session.next()
portrait = session.finish()
print(portrait.to_dict())
```

## `get_methodologies() -> list[Methodology]`

Возвращает все подключённые методики (m01–m20) в порядке прохождения опроса.

## `SurveySession(methodologies)`

Создаёт один проход опроса. При создании собирает вопросы всех методик.
Если методика не смогла выдать вопросы, она не ломает опрос: её вопросы не показываются,
а причина записывается в `session.failed`.

| Атрибут | Тип | Описание |
|---------|-----|----------|
| `questions` | `list[Question]` | Все вопросы модуля по порядку, блоками по методикам |
| `answers` | `dict[str, Answer]` | Данные пользователем ответы: id вопроса → ответ |
| `failed` | `dict[str, str]` | Методики, вопросы которых не загрузились: id → причина |
| `position` | `int` | Индекс текущего вопроса |

### Навигация

| Метод | Возвращает | Описание |
|-------|-----------|----------|
| `current_question()` | `Question \| None` | Текущий вопрос; `None` — вопросы закончились |
| `next()` | `Question \| None` | Переход к следующему вопросу. После последнего — `None`, дальше не уходит |
| `back()` | `Question \| None` | Переход к предыдущему вопросу. На первом вопросе остаётся на месте; после конца опроса возвращает к последнему вопросу |
| `progress()` | `(int, int)` | (номер текущего вопроса с 1, всего вопросов) — для индикатора прогресса |
| `is_finished()` | `bool` | `True`, когда пользователь прошёл последний вопрос |

### Ответы

| Метод | Описание | Ошибки |
|-------|----------|--------|
| `answer(value)` | Сохраняет ответ на текущий вопрос. Повторный ответ перезаписывает прежний. `None` — то же, что `skip()`. **Не переходит** к следующему вопросу | `ValueError`: такого варианта нет, неверный тип ответа, опрос уже пройден |
| `skip()` | Пропускает текущий вопрос (`Answer` с `value=None`). **Не переходит** к следующему вопросу | `ValueError`: вопрос обязательный (`required=True`), опрос уже пройден |
| `grouped_answers()` | Ответы, сгруппированные по методикам: id методики → {id вопроса → ответ}. Вопросы без ответа считаются пропущенными | — |
| `finish()` | Передаёт ответы в сборщик и возвращает `Portrait`. Можно вызывать в любой момент, в том числе на середине опроса | — |

Допустимые значения `value`:

| Тип вопроса | `value` | Пример |
|-------------|---------|--------|
| `scale` | одно число из `options` | `4` |
| `single` | одно число из `options` | `2` |
| `multiple` | непустой список разных чисел из `options` | `[1, 3]` |

## `collect(methodologies, grouped_answers, failed) -> Portrait`

Собирает итоговый отчёт. Обычно вызывается через `session.finish()`.

- В отчёте ровно один результат на каждую методику, в порядке `methodologies`.
- Методика из `failed` → результат со статусом `error`.
- Методика без единого ответа → `missing`.
- Методика упала или вернула результат не по контракту → `error`, причина в `message`.
- Одна и та же методика подключена дважды → `ValueError`.

## `Portrait.to_dict() -> dict`

Отчёт в виде словаря для сохранения в JSON. Примеры — в [report-examples.md](report-examples.md).

## Консольная демонстрация

```bash
python -m app.demo            # пройти опрос самому
python -m app.demo --auto     # случайные ответы
python -m app.demo --json     # отчёт в JSON
```
