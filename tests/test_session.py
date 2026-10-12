import pytest

from app.contracts import ResultStatus
from app.engine.session import SurveySession
from app.methodologies.stubs import StubMethodology
from tests.fakes import MixedQuestionsMethodology, NoQuestionsMethodology


def make_session(*methodologies):
    return SurveySession(list(methodologies) or [
        StubMethodology("m01", "Первая", 2),
        StubMethodology("m02", "Вторая", 3),
    ])


def test_questions_go_in_blocks_by_methodology():
    session = make_session()
    assert [q.id for q in session.questions] == ["m01.1", "m01.2", "m02.1", "m02.2", "m02.3"]


def test_navigation_forward_to_end():
    session = make_session()
    assert session.current_question().id == "m01.1"
    seen = [session.current_question().id]
    while (question := session.next()) is not None:
        seen.append(question.id)
    assert seen == ["m01.1", "m01.2", "m02.1", "m02.2", "m02.3"]
    assert session.is_finished()
    assert session.next() is None  # дальше конца не уходим


def test_back_on_first_question_stays():
    session = make_session()
    assert session.back().id == "m01.1"


def test_back_from_end_returns_to_last_question():
    session = make_session()
    while session.next() is not None:
        pass
    assert session.back().id == "m02.3"
    assert not session.is_finished()


def test_progress():
    session = make_session()
    assert session.progress() == (1, 5)
    session.next()
    assert session.progress() == (2, 5)
    while session.next() is not None:
        pass
    assert session.progress() == (5, 5)


def test_answer_and_overwrite():
    session = make_session()
    session.answer(2)
    session.answer(4)
    assert session.answers["m01.1"].value == 4


def test_answer_does_not_move_forward():
    session = make_session()
    session.answer(3)
    assert session.current_question().id == "m01.1"


@pytest.mark.parametrize("value", [0, 6, "3", 2.5, True, [3]])
def test_invalid_scale_answer_rejected(value):
    session = make_session()
    with pytest.raises(ValueError):
        session.answer(value)
    assert "m01.1" not in session.answers


def test_multiple_choice_answer():
    session = make_session(MixedQuestionsMethodology("m01", "Смешанная"))
    session.answer(1)
    session.next()
    session.answer([1, 3])
    assert session.answers["m01.2"].value == [1, 3]


@pytest.mark.parametrize("value", [[], [1, 1], [4], 1, [True]])
def test_invalid_multiple_choice_rejected(value):
    session = make_session(MixedQuestionsMethodology("m01", "Смешанная"))
    session.next()
    with pytest.raises(ValueError):
        session.answer(value)


def test_skip_saves_none():
    session = make_session()
    session.skip()
    assert session.answers["m01.1"].skipped


def test_answer_none_is_skip():
    session = make_session()
    session.answer(None)
    assert session.answers["m01.1"].skipped


def test_required_question_cannot_be_skipped():
    session = make_session(MixedQuestionsMethodology("m01", "Смешанная"))
    with pytest.raises(ValueError):
        session.skip()


def test_answer_after_finish_rejected():
    session = make_session(StubMethodology("m01", "Первая", 1))
    session.next()
    with pytest.raises(ValueError):
        session.answer(3)


def test_grouped_answers_fill_unanswered_with_none():
    session = make_session()
    session.answer(5)          # m01.1
    session.next()
    session.skip()             # m01.2
    session.next()
    session.answer(1)          # m02.1, дальше пользователь остановился

    grouped = session.grouped_answers()
    assert list(grouped) == ["m01", "m02"]
    assert {q: a.value for q, a in grouped["m01"].items()} == {"m01.1": 5, "m01.2": None}
    assert {q: a.value for q, a in grouped["m02"].items()} == {"m02.1": 1, "m02.2": None, "m02.3": None}


def test_broken_methodology_is_excluded_but_survey_continues():
    session = make_session(
        StubMethodology("m01", "Первая", 2),
        NoQuestionsMethodology("m02", "Сломанная"),
        StubMethodology("m03", "Третья", 1),
    )
    assert [q.id for q in session.questions] == ["m01.1", "m01.2", "m03.1"]
    assert "m02" in session.failed


def test_full_pass_gives_portrait():
    session = make_session()
    while not session.is_finished():
        session.answer(5)
        session.next()
    portrait = session.finish()
    assert [r.methodology_id for r in portrait.results] == ["m01", "m02"]
    assert all(r.status == ResultStatus.OK for r in portrait.results)
    assert portrait.results[1].scales[0].score == 15


def test_stop_in_the_middle_gives_missing_for_untouched_methodology():
    session = make_session()
    session.answer(3)
    portrait = session.finish()
    assert portrait.results[0].status == ResultStatus.OK
    assert portrait.results[1].status == ResultStatus.MISSING
