"""Список методик, подключённых к модулю, в порядке прохождения опроса."""

from app.methodologies.base import Methodology
from app.methodologies.stubs import StubMethodology


def get_methodologies() -> list[Methodology]:
    # Этап 1: заглушки. На этапе 2 здесь будут 20 настоящих методик (m01–m20).
    return [
        StubMethodology("m01", "Оценка особенностей личности"),
        StubMethodology("m02", "Индекс устойчивости идентичности"),
        StubMethodology("m03", "Критическое мышление"),
    ]
