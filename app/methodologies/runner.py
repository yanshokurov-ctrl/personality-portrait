"""Безопасный вызов методик.

Ошибка в одной методике не должна ронять весь опрос: любое исключение
или нарушение контракта превращается в результат со статусом ERROR.
"""

from app.contracts import Answer, MethodologyResult, Question, ResultStatus, ScaleResult
from app.methodologies.base import Methodology


def load_questions(methodology: Methodology) -> tuple[list[Question], str | None]:
    """Получить вопросы методики. Возвращает (вопросы, None) или ([], причина ошибки)."""
    try:
        questions = list(methodology.get_questions())
    except Exception as exc:
        return [], f"не удалось получить вопросы: {exc!r}"

    if not questions:
        return [], "методика не вернула ни одного вопроса"
    for question in questions:
        if not isinstance(question, Question):
            return [], f"вопрос неверного типа: {type(question).__name__}"
        if question.methodology_id != methodology.id:
            return [], f"вопрос {question.id} относится к методике {question.methodology_id}"
    return questions, None


def check_result(methodology: Methodology, result: object) -> list[str]:
    """Проверить, что результат соответствует контракту. Возвращает список проблем."""
    if not isinstance(result, MethodologyResult):
        return [f"результат неверного типа: {type(result).__name__}"]

    problems = []
    if result.methodology_id != methodology.id:
        problems.append(f"чужой methodology_id: {result.methodology_id}")
    if result.status == ResultStatus.OK and not result.scales:
        problems.append("нет ни одной шкалы")
    for scale in result.scales:
        if not isinstance(scale, ScaleResult):
            problems.append(f"шкала неверного типа: {type(scale).__name__}")
            continue
        if isinstance(scale.score, bool) or not isinstance(scale.score, (int, float)):
            problems.append(f"шкала {scale.scale_id}: балл не является числом")
        if not scale.interpretation:
            problems.append(f"шкала {scale.scale_id}: пустая интерпретация")
    return problems


def run_methodology(methodology: Methodology, answers: dict[str, Answer]) -> MethodologyResult:
    """Обработать ответы методикой, не пропуская наружу её ошибки."""
    if all(answer.skipped for answer in answers.values()):
        return MethodologyResult(
            methodology.id, methodology.name, ResultStatus.MISSING,
            message="Нет ответов на вопросы методики",
        )

    try:
        result = methodology.process(answers)
    except Exception as exc:
        return _error(methodology, f"ошибка при обработке: {exc!r}")

    problems = check_result(methodology, result)
    if problems:
        return _error(methodology, "неверный формат результата: " + "; ".join(problems))
    return result


def _error(methodology: Methodology, reason: str) -> MethodologyResult:
    return MethodologyResult(methodology.id, methodology.name, ResultStatus.ERROR, message=reason)
