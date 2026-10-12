"""Заглушки методик для этапа 1.

Нужны, чтобы движок и сборщик можно было разрабатывать и тестировать
до того, как появятся настоящие методики (этап 2).
"""

from app.contracts import (
    Answer, Level, MethodologyResult, Option, Question, QuestionType,
    ResultStatus, ScaleResult,
)
from app.methodologies.base import Methodology

SCALE_OPTIONS = tuple(
    Option(value, text)
    for value, text in [
        (1, "Совсем не согласен"),
        (2, "Скорее не согласен"),
        (3, "Затрудняюсь ответить"),
        (4, "Скорее согласен"),
        (5, "Полностью согласен"),
    ]
)

INTERPRETATIONS = {
    Level.LOW: "Низкий уровень выраженности характеристики.",
    Level.MEDIUM: "Средний уровень выраженности характеристики.",
    Level.HIGH: "Высокий уровень выраженности характеристики.",
}


class StubMethodology(Methodology):
    """Методика-заглушка: N вопросов со шкалой 1–5, балл — сумма ответов."""

    def __init__(self, id: str, name: str, question_count: int = 3):
        self.id = id
        self.name = name
        self.question_count = question_count

    def get_questions(self) -> list[Question]:
        return [
            Question(
                id=f"{self.id}.{number}",
                methodology_id=self.id,
                text=f"[{self.name}] Тестовое утверждение № {number}",
                type=QuestionType.SCALE,
                options=SCALE_OPTIONS,
            )
            for number in range(1, self.question_count + 1)
        ]

    def process(self, answers: dict[str, Answer]) -> MethodologyResult:
        score = sum(a.value for a in answers.values() if not a.skipped)
        max_score = 5 * self.question_count
        if score < max_score / 3:
            level = Level.LOW
        elif score < 2 * max_score / 3:
            level = Level.MEDIUM
        else:
            level = Level.HIGH
        scale = ScaleResult("total", "Общий балл", score, level, INTERPRETATIONS[level])
        return MethodologyResult(self.id, self.name, ResultStatus.OK, [scale])
