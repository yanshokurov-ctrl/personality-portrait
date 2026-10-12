# Как подключить методику

Инструкция для этапа 2: как заменить заглушку настоящей методикой.

## 1. Создать класс методики

Файл: `app/methodologies/m06_cope.py` (номер и короткое имя методики).
Класс наследуется от `Methodology` и реализует два метода.

```python
from app.contracts import (
    Answer, Level, MethodologyResult, Option, Question, QuestionType,
    ResultStatus, ScaleResult,
)
from app.methodologies.base import Methodology


class CopeMethodology(Methodology):
    id = "m06"                 # номер из списка методик — менять нельзя
    name = "Методика COPE"

    def get_questions(self) -> list[Question]:
        options = (Option(1, "Никогда"), Option(2, "Иногда"), Option(3, "Часто"), Option(4, "Всегда"))
        return [
            Question("m06.1", self.id, "Текст вопроса 1", QuestionType.SCALE, options),
            Question("m06.2", self.id, "Текст вопроса 2", QuestionType.SCALE, options),
        ]

    def process(self, answers: dict[str, Answer]) -> MethodologyResult:
        score = sum(a.value for a in answers.values() if not a.skipped)
        level = Level.HIGH if score >= 6 else Level.LOW
        return MethodologyResult(self.id, self.name, ResultStatus.OK, [
            ScaleResult("coping", "Совладание", score, level, "Текст интерпретации"),
        ])
```

## 2. Правила, которые нужно соблюдать

| Правило | Почему |
|---------|--------|
| `id` вопроса — `"<id методики>.<номер>"`, например `"m06.12"` | id должны быть уникальны во всём модуле |
| `methodology_id` каждого вопроса равен `id` методики | иначе методика отключается как ошибочная |
| `process()` получает ответы **только своей** методики, включая пропущенные (`value=None`) | пропуски нужно учитывать самостоятельно |
| Вернуть `ResultStatus.OK` и хотя бы одну шкалу | иначе результат считается ошибкой |
| `score` — число, `interpretation` — непустой текст | проверяется автоматически |
| Несколько шкал — несколько `ScaleResult` в списке | у одной методики может быть много шкал |
| Не ловить все исключения внутри `process()` «на всякий случай» | ошибки и так перехватываются ядром и попадают в отчёт |
| Вопросы и ключи — в JSON в `app/methodologies/data/` (формат будет утверждён на этапе 2) | данные проще проверять отдельно от кода |

Если все вопросы методики пропущены, `process()` не вызывается — ядро само ставит статус `missing`.

## 3. Подключить в список методик

В `app/methodologies/registry.py` заменить заглушку с тем же `id` на новый класс.
Порядок в списке = порядок методик в опросе.

## 4. Проверить

```bash
pytest
python -m app.demo
```

- Тесты должны проходить, в том числе `tests/test_registry.py` (все 20 методик на месте).
- Добавить тесты своей методики: `tests/test_m06_cope.py` — примеры
  «ответил так-то → балл такой-то» по ключам.
- В демонстрации пройти свою методику и проверить, что результат совпадает с ключом.
