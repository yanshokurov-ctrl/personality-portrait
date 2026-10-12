"""Движок опроса: один проход опроса пользователем.

Движок не содержит логики конкретных методик: он работает только
с общим потоком вопросов и ответов (контракты из app.contracts).
"""

from app.contracts import Answer, AnswerValue, Question
from app.methodologies.base import Methodology
from app.methodologies.runner import load_questions


class SurveySession:
    def __init__(self, methodologies: list[Methodology]):
        self.methodologies = list(methodologies)
        self.questions: list[Question] = []  # все вопросы модуля по порядку, блоками по методикам
        self.failed: dict[str, str] = {}     # id методики -> почему её вопросы не загрузились
        self.answers: dict[str, Answer] = {}  # id вопроса -> ответ
        self.position = 0                     # индекс текущего вопроса в self.questions

        # Методика, которая не отдала вопросы, пропускается, а опрос продолжается.
        for methodology in self.methodologies:
            questions, error = load_questions(methodology)
            if error:
                self.failed[methodology.id] = error
            else:
                self.questions.extend(questions)

    # ----- Задача 1.4 (Разработчик 1): показ вопросов и навигация -----

    def current_question(self) -> Question | None:
        """Текущий вопрос или None, если вопросы закончились."""
        raise NotImplementedError

    def next(self) -> Question | None:
        """Перейти к следующему вопросу и вернуть его (None — вопросы закончились)."""
        raise NotImplementedError

    def back(self) -> Question | None:
        """Вернуться к предыдущему вопросу. На первом вопросе остаёмся на месте."""
        raise NotImplementedError

    def progress(self) -> tuple[int, int]:
        """(номер текущего вопроса начиная с 1, всего вопросов) — для индикатора прогресса."""
        raise NotImplementedError

    def is_finished(self) -> bool:
        """True, когда пользователь прошёл последний вопрос."""
        raise NotImplementedError

    # ----- Задача 1.5 (Разработчик 2): приём и группировка ответов -----

    def answer(self, value: AnswerValue) -> None:
        """Сохранить ответ на текущий вопрос (повторный ответ перезаписывает прежний).

        Проверить, что value допустим для типа вопроса и есть среди вариантов,
        иначе выбросить ValueError.
        """
        raise NotImplementedError

    def skip(self) -> None:
        """Пропустить текущий вопрос (сохраняется Answer с value=None)."""
        raise NotImplementedError

    def grouped_answers(self) -> dict[str, dict[str, Answer]]:
        """Ответы, сгруппированные по методикам: id методики -> {id вопроса -> ответ}.

        Вопросы, до которых пользователь не дошёл, считаются пропущенными (value=None),
        чтобы каждая методика получила ответы на ВСЕ свои вопросы.
        """
        raise NotImplementedError
