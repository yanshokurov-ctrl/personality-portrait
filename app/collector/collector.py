"""Сборщик результатов: формирует итоговый отчёт «Портрет личности»."""

from app.contracts import Answer, Portrait
from app.methodologies.base import Methodology


def collect(
    methodologies: list[Methodology],
    grouped_answers: dict[str, dict[str, Answer]],
    failed: dict[str, str],
) -> Portrait:
    """Задача 1.6 (Разработчик 3).

    Правила:
    - в отчёте ровно один результат на каждую методику, в порядке methodologies —
      без потерь и дубликатов;
    - методика из failed (не загрузились вопросы) -> результат со статусом ERROR
      и причиной в message;
    - остальные обрабатываются через app.methodologies.runner.run_methodology,
      который сам вернёт ERROR или MISSING при проблемах;
    - методики нет в grouped_answers -> передать ей пустой словарь ответов.
    """
    raise NotImplementedError
