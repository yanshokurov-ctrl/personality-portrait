"""Консольная демонстрация ядра модуля (до появления интерфейса на этапе 3).

Запуск:
    python -m app.demo           — пройти опрос самому
    python -m app.demo --auto    — случайные ответы, сразу показать отчёт
    python -m app.demo --json    — вывести отчёт в формате JSON
"""

import argparse
import json
import random
import sys

from app.contracts import Portrait, Question, QuestionType, ResultStatus
from app.engine.session import SurveySession
from app.methodologies.registry import get_methodologies

LEVELS = {"low": "низкий", "medium": "средний", "high": "высокий"}

# Русская и английская раскладка — чтобы не переключать язык.
SKIP, BACK, QUIT = {"п", "s"}, {"н", "b"}, {"в", "q"}


def run_interactive(session: SurveySession) -> bool:
    """Провести опрос в консоли. Возвращает False, если пользователь вышел досрочно."""
    while not session.is_finished():
        question = session.current_question()
        current, total = session.progress()
        print(f"\nВопрос {current} из {total}")
        print(question.text)
        for option in question.options:
            print(f"  {option.value}. {option.text}")

        hint = "номера через пробел" if question.type == QuestionType.MULTIPLE else "номер"
        try:
            raw = input(f"Ответ ({hint}; п — пропустить, н — назад, в — завершить): ").strip().lower()
        except (EOFError, KeyboardInterrupt):  # конец ввода или Ctrl+C — как «завершить»
            return False
        if raw in QUIT:
            return False
        if raw in BACK:
            session.back()
            continue
        try:
            if raw in SKIP:
                session.skip()
            else:
                session.answer(_parse(question, raw))
        except ValueError as exc:
            print(f"! {exc}")
            continue
        session.next()
    return True


def run_auto(session: SurveySession, rng: random.Random) -> None:
    """Пройти опрос случайными ответами (примерно 10% вопросов пропускается)."""
    while not session.is_finished():
        question = session.current_question()
        values = [option.value for option in question.options]
        if not question.required and rng.random() < 0.1:
            session.skip()
        elif question.type == QuestionType.MULTIPLE:
            session.answer(rng.sample(values, rng.randint(1, len(values))))
        else:
            session.answer(rng.choice(values))
        session.next()


def format_portrait(portrait: Portrait) -> str:
    lines = ["", "=" * 60, "ПОРТРЕТ ЛИЧНОСТИ", f"Дата: {portrait.created_at}", "=" * 60]
    for number, result in enumerate(portrait.results, start=1):
        lines.append(f"\n{number}. {result.name}")
        if result.status == ResultStatus.MISSING:
            lines.append("   Вы не ответили на вопросы этой методики.")
        elif result.status == ResultStatus.ERROR:
            lines.append("   Результат по методике временно недоступен.")
        for scale in result.scales:
            level = f", уровень: {LEVELS[scale.level]}" if scale.level else ""
            lines.append(f"   {scale.name}: {scale.score:g}{level}")
            lines.append(f"   {scale.interpretation}")

    counts = {status: sum(r.status == status for r in portrait.results) for status in ResultStatus}
    lines.append(
        f"\nИтого: обработано {counts[ResultStatus.OK]}, без ответов {counts[ResultStatus.MISSING]}, "
        f"с ошибкой {counts[ResultStatus.ERROR]} из {len(portrait.results)}"
    )
    return "\n".join(lines)


def _parse(question: Question, raw: str):
    try:
        if question.type == QuestionType.MULTIPLE:
            return [int(part) for part in raw.replace(",", " ").split()]
        return int(raw)
    except ValueError:
        raise ValueError("Введите номер варианта") from None


def main() -> None:
    parser = argparse.ArgumentParser(description="Демонстрация модуля «Портрет личности»")
    parser.add_argument("--auto", action="store_true", help="случайные ответы")
    parser.add_argument("--seed", type=int, help="зерно для --auto (одинаковые ответы при повторе)")
    parser.add_argument("--json", action="store_true", help="вывести отчёт в JSON")
    args = parser.parse_args()

    # Русский текст при перенаправлении ввода/вывода в Windows (по умолчанию там cp1251).
    for stream in (sys.stdin, sys.stdout):
        stream.reconfigure(encoding="utf-8")

    session = SurveySession(get_methodologies())
    for methodology_id, reason in session.failed.items():
        print(f"! Методика {methodology_id} отключена: {reason}")

    if args.auto:
        run_auto(session, random.Random(args.seed))
    elif not run_interactive(session):
        print("\nОпрос завершён досрочно — непройденные вопросы считаются пропущенными.")

    portrait = session.finish()
    if args.json:
        print(json.dumps(portrait.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(format_portrait(portrait))


if __name__ == "__main__":
    main()
