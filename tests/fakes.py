"""«Сломанные» методики для проверки обработки ошибок."""

from app.contracts import MethodologyResult, ResultStatus
from app.methodologies.stubs import StubMethodology


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
