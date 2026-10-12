import random

from app.demo import format_portrait, run_auto, run_interactive
from app.engine.session import SurveySession
from app.methodologies.stubs import StubMethodology
from tests.fakes import MixedQuestionsMethodology


def feed(monkeypatch, *inputs):
    answers = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))


def test_interactive_full_pass(monkeypatch, capsys):
    session = SurveySession([StubMethodology("m01", "Первая", 2)])
    feed(monkeypatch, "5", "4")
    assert run_interactive(session) is True
    assert session.grouped_answers()["m01"]["m01.2"].value == 4


def test_interactive_back_skip_and_bad_input(monkeypatch, capsys):
    session = SurveySession([StubMethodology("m01", "Первая", 2)])
    feed(monkeypatch, "abc", "9", "1", "н", "2", "п")
    assert run_interactive(session) is True
    answers = session.grouped_answers()["m01"]
    assert answers["m01.1"].value == 2  # исправлено после возврата назад
    assert answers["m01.2"].skipped
    assert "Введите номер варианта" in capsys.readouterr().out


def test_interactive_multiple_choice(monkeypatch):
    session = SurveySession([MixedQuestionsMethodology("m01", "Смешанная")])
    feed(monkeypatch, "1", "1, 3")
    run_interactive(session)
    assert session.answers["m01.2"].value == [1, 3]


def test_interactive_quit(monkeypatch):
    session = SurveySession([StubMethodology("m01", "Первая", 2)])
    feed(monkeypatch, "3", "в")
    assert run_interactive(session) is False
    assert not session.is_finished()


def test_interactive_end_of_input_is_quit(monkeypatch):
    session = SurveySession([StubMethodology("m01", "Первая", 2)])

    def no_more_input(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", no_more_input)
    assert run_interactive(session) is False


def test_auto_pass_and_report():
    session = SurveySession([StubMethodology("m01", "Первая"), MixedQuestionsMethodology("m02", "Смешанная")])
    run_auto(session, random.Random(1))
    assert session.is_finished()
    text = format_portrait(session.finish())
    assert "ПОРТРЕТ ЛИЧНОСТИ" in text
    assert "1. Первая" in text and "2. Смешанная" in text
