"""Контракты данных модуля.

Все компоненты (движок, методики, сборщик, интерфейс, валидатор) обмениваются
только этими структурами. Менять их можно только через основного разработчика.

ЧЕРНОВИК: будет сверен с контрактами, утверждёнными преподавателем.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum


class QuestionType(StrEnum):
    SINGLE = "single"      # один вариант из списка
    MULTIPLE = "multiple"  # несколько вариантов из списка
    SCALE = "scale"        # оценка по шкале, например 1–5


@dataclass(frozen=True)
class Option:
    value: int  # то, что уходит в ключ методики
    text: str   # то, что видит пользователь


@dataclass(frozen=True)
class Question:
    id: str  # уникален в модуле: "<id методики>.<номер>", например "m01.5"
    methodology_id: str
    text: str
    type: QuestionType
    options: tuple[Option, ...] = ()
    required: bool = True


# int — один вариант или шкала, list[int] — несколько вариантов, None — вопрос пропущен
AnswerValue = int | list[int] | None


@dataclass
class Answer:
    question_id: str
    value: AnswerValue

    @property
    def skipped(self) -> bool:
        return self.value is None


class Level(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ScaleResult:
    """Результат по одной шкале методики (у многих методик шкал несколько)."""

    scale_id: str
    name: str
    score: float
    level: Level | None  # None, если у шкалы нет уровней
    interpretation: str


class ResultStatus(StrEnum):
    OK = "ok"            # методика обработана
    ERROR = "error"      # методика упала или вернула результат в неверном формате
    MISSING = "missing"  # пользователь не ответил ни на один вопрос методики


@dataclass
class MethodologyResult:
    methodology_id: str
    name: str
    status: ResultStatus
    scales: list[ScaleResult] = field(default_factory=list)
    message: str = ""  # причина ошибки или пометка для пользователя


@dataclass
class Portrait:
    """Итоговый отчёт «Портрет личности»."""

    results: list[MethodologyResult]
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def to_dict(self) -> dict:
        return asdict(self)
