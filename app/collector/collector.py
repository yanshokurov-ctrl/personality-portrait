"""Сборщик результатов: формирует итоговый отчёт «Портрет личности»."""

from app.contracts import Answer, MethodologyResult, Portrait, ResultStatus
from app.methodologies.base import Methodology
from app.methodologies.runner import run_methodology


def collect(
    methodologies: list[Methodology],
    grouped_answers: dict[str, dict[str, Answer]],
    failed: dict[str, str],
) -> Portrait:
    """Собрать результаты всех методик в итоговый отчёт.

    В отчёте ровно один результат на каждую методику, в порядке methodologies.
    Ошибка одной методики не мешает остальным: она попадает в отчёт со статусом ERROR.
    """
    ids = [methodology.id for methodology in methodologies]
    duplicates = sorted({id for id in ids if ids.count(id) > 1})
    if duplicates:
        raise ValueError(f"Методики подключены повторно: {', '.join(duplicates)}")

    results = []
    for methodology in methodologies:
        if methodology.id in failed:
            results.append(MethodologyResult(
                methodology.id, methodology.name, ResultStatus.ERROR,
                message=f"Вопросы методики не загрузились: {failed[methodology.id]}",
            ))
        else:
            results.append(run_methodology(methodology, grouped_answers.get(methodology.id, {})))
    return Portrait(results)
