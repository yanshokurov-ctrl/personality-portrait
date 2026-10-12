from app.contracts import Answer, Level, ResultStatus
from app.methodologies.runner import load_questions, run_methodology
from app.methodologies.stubs import StubMethodology
from tests.fakes import (
    CrashingMethodology, EmptyScalesMethodology, NoQuestionsMethodology, WrongTypeMethodology,
)


def answers_for(methodology, values):
    questions = methodology.get_questions()
    return {q.id: Answer(q.id, v) for q, v in zip(questions, values)}


def test_stub_questions_follow_contract():
    stub = StubMethodology("m01", "Тест", question_count=4)
    questions, error = load_questions(stub)
    assert error is None
    assert [q.id for q in questions] == ["m01.1", "m01.2", "m01.3", "m01.4"]


def test_stub_result_ok():
    stub = StubMethodology("m01", "Тест")
    result = run_methodology(stub, answers_for(stub, [5, 5, 5]))
    assert result.status == ResultStatus.OK
    assert result.scales[0].score == 15
    assert result.scales[0].level == Level.HIGH


def test_stub_low_level():
    stub = StubMethodology("m01", "Тест")
    result = run_methodology(stub, answers_for(stub, [1, 1, 1]))
    assert result.scales[0].level == Level.LOW


def test_partially_skipped_answers_are_processed():
    stub = StubMethodology("m01", "Тест")
    result = run_methodology(stub, answers_for(stub, [5, None, 5]))
    assert result.status == ResultStatus.OK
    assert result.scales[0].score == 10


def test_all_skipped_gives_missing():
    stub = StubMethodology("m01", "Тест")
    result = run_methodology(stub, answers_for(stub, [None, None, None]))
    assert result.status == ResultStatus.MISSING


def test_no_answers_gives_missing():
    result = run_methodology(StubMethodology("m01", "Тест"), {})
    assert result.status == ResultStatus.MISSING


def test_crash_gives_error_instead_of_exception():
    methodology = CrashingMethodology("m01", "Тест")
    result = run_methodology(methodology, answers_for(methodology, [3, 3, 3]))
    assert result.status == ResultStatus.ERROR
    assert "сбой методики" in result.message


def test_wrong_result_type_gives_error():
    methodology = WrongTypeMethodology("m01", "Тест")
    result = run_methodology(methodology, answers_for(methodology, [3, 3, 3]))
    assert result.status == ResultStatus.ERROR
    assert "неверного типа" in result.message


def test_ok_without_scales_gives_error():
    methodology = EmptyScalesMethodology("m01", "Тест")
    result = run_methodology(methodology, answers_for(methodology, [3, 3, 3]))
    assert result.status == ResultStatus.ERROR


def test_failing_questions_reported():
    questions, error = load_questions(NoQuestionsMethodology("m01", "Тест"))
    assert questions == []
    assert "вопросы недоступны" in error
