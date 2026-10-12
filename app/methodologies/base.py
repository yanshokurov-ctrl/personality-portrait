from abc import ABC, abstractmethod

from app.contracts import Answer, MethodologyResult, Question


class Methodology(ABC):
    """Интерфейс, который реализует каждая методика.

    Движок знает о методике только это: id, название, список вопросов
    и функцию обработки ответов. Логика подсчёта — целиком внутри методики.
    """

    id: str    # "m01" … "m20"
    name: str  # название из списка методик

    @abstractmethod
    def get_questions(self) -> list[Question]:
        """Вопросы методики в порядке показа.

        У каждого вопроса methodology_id == self.id, а id имеет вид "<self.id>.<номер>".
        """

    @abstractmethod
    def process(self, answers: dict[str, Answer]) -> MethodologyResult:
        """Обработать ответы пользователя на вопросы ЭТОЙ методики.

        answers: id вопроса -> ответ; пропущенные вопросы приходят с value=None.
        Возвращает результат со status=OK и хотя бы одной шкалой.
        """
