"""«Сломанные» методики для проверки обработки ошибок."""

from app.contracts import MethodologyResult, Option, Question, QuestionType, ResultStatus
from app.methodologies.stubs import StubMethodology


class MixedQuestionsMethodology(StubMethodology):
    """Вопросы разных типов: обязательный с одним вариантом и с несколькими вариантами."""

    def get_questions(self):
        options = (Option(1, "А"), Option(2, "Б"), Option(3, "В"))
        return [
            Question(f"{self.id}.1", self.id, "Один вариант", QuestionType.SINGLE, options, required=True),
            Question(f"{self.id}.2", self.id, "Несколько вариантов", QuestionType.MULTIPLE, options),
        ]


class CrashingMethodology(StubMethodology):
    """Падает при обработке ответов."""

    def process(self, answers):
        raise RuntimeError("сбой методики")


class NoQuestionsMethodology(StubMethodology):
    """Падает при запросе вопросов."""

    def get_questions(self):
        raise RuntimeError("вопросы недоступны")


class WrongTypeMethodology(StubMethodology):
    """Возвращает результат не по контракту."""

    def process(self, answers):
        return {"score": 10}


class EmptyScalesMethodology(StubMethodology):
    """Возвращает OK без единой шкалы."""

    def process(self, answers):
        return MethodologyResult(self.id, self.name, ResultStatus.OK)
