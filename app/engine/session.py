"""Движок опроса: один проход опроса пользователем.

Движок не содержит логики конкретных методик: он работает только
с общим потоком вопросов и ответов (контракты из app.contracts).
"""

from app.collector.collector import collect
from app.contracts import Answer, AnswerValue, Portrait, Question, QuestionType
from app.methodologies.base import Methodology
from app.methodologies.runner import load_questions


class SurveySession:
    def __init__(self, methodologies: list[Methodology]):
        self.methodologies = list(methodologies)
        self.questions: list[Question] = []  # все вопросы модуля по порядку, блоками по методикам
        self.failed: dict[str, str] = {}     # id методики -> почему её вопросы не загрузились
        self.answers: dict[str, Answer] = {}  # id вопроса -> ответ
        self.position = 0                     # индекс текущего вопроса; len(questions) — опрос пройден

        # Методика, которая не отдала вопросы, пропускается, а опрос продолжается.
        for methodology in self.methodologies:
            questions, error = load_questions(methodology)
            if error:
                self.failed[methodology.id] = error
            else:
                self.questions.extend(questions)

    # ----- Показ вопросов и навигация -----

    def current_question(self) -> Question | None:
        """Текущий вопрос или None, если вопросы закончились."""
        if self.is_finished():
            return None
        return self.questions[self.position]

    def next(self) -> Question | None:
        """Перейти к следующему вопросу и вернуть его (None — вопросы закончились)."""
        if not self.is_finished():
            self.position += 1
        return self.current_question()

    def back(self) -> Question | None:
        """Вернуться к предыдущему вопросу. На первом вопросе остаёмся на месте."""
        if self.position > 0:
            self.position -= 1
        return self.current_question()

    def progress(self) -> tuple[int, int]:
        """(номер текущего вопроса начиная с 1, всего вопросов) — для индикатора прогресса."""
        total = len(self.questions)
        return min(self.position + 1, total), total

    def is_finished(self) -> bool:
        """True, когда пользователь прошёл последний вопрос."""
        return self.position >= len(self.questions)

    # ----- Приём и группировка ответов -----

    def answer(self, value: AnswerValue) -> None:
        """Сохранить ответ на текущий вопрос (повторный ответ перезаписывает прежний).

        Не переходит к следующему вопросу — для этого интерфейс вызывает next().
        None означает пропуск вопроса (то же, что skip()).
        Выбрасывает ValueError, если ответ недопустим или опрос уже пройден.
        """
        question = self._require_current()
        if value is None:
            self.skip()
            return
        _check_value(question, value)
        self.answers[question.id] = Answer(question.id, value)

    def skip(self) -> None:
        """Пропустить текущий вопрос (сохраняется Answer с value=None).

        Обязательный вопрос (required=True) пропустить нельзя — ValueError.
        """
        question = self._require_current()
        if question.required:
            raise ValueError(f"Вопрос {question.id} обязателен, его нельзя пропустить")
        self.answers[question.id] = Answer(question.id, None)

    def grouped_answers(self) -> dict[str, dict[str, Answer]]:
        """Ответы, сгруппированные по методикам: id методики -> {id вопроса -> ответ}.

        Вопросы, до которых пользователь не дошёл, считаются пропущенными (value=None),
        чтобы каждая методика получила ответы на ВСЕ свои вопросы.
        """
        grouped: dict[str, dict[str, Answer]] = {}
        for question in self.questions:
            answer = self.answers.get(question.id) or Answer(question.id, None)
            grouped.setdefault(question.methodology_id, {})[question.id] = answer
        return grouped

    def finish(self) -> Portrait:
        """Передать ответы в сборщик и получить итоговый «Портрет личности»."""
        return collect(self.methodologies, self.grouped_answers(), self.failed)

    def _require_current(self) -> Question:
        question = self.current_question()
        if question is None:
            raise ValueError("Опрос уже пройден: нет текущего вопроса")
        return question


def _check_value(question: Question, value: AnswerValue) -> None:
    """Проверить, что ответ подходит к типу вопроса и есть среди вариантов."""
    allowed = {option.value for option in question.options}

    if question.type == QuestionType.MULTIPLE:
        if not isinstance(value, list) or not value:
            raise ValueError(f"Вопрос {question.id}: нужен непустой список вариантов")
        if len(set(value)) != len(value):
            raise ValueError(f"Вопрос {question.id}: варианты повторяются")
        chosen = value
    else:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"Вопрос {question.id}: нужен один вариант (число)")
        chosen = [value]

    for item in chosen:
        if isinstance(item, bool) or not isinstance(item, int) or item not in allowed:
            raise ValueError(f"Вопрос {question.id}: недопустимый вариант {item!r}")
