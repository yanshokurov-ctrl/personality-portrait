from app.contracts import ResultStatus
from app.engine.session import SurveySession
from app.methodologies.registry import METHODOLOGY_NAMES, get_methodologies


def test_all_20_methodologies_connected():
    methodologies = get_methodologies()
    assert [m.id for m in methodologies] == [f"m{n:02d}" for n in range(1, 21)]
    assert [m.name for m in methodologies] == METHODOLOGY_NAMES


def test_question_ids_unique_across_module():
    session = SurveySession(get_methodologies())
    ids = [q.id for q in session.questions]
    assert len(ids) == len(set(ids))
    assert not session.failed


def test_full_pass_through_all_20_methodologies():
    session = SurveySession(get_methodologies())
    while not session.is_finished():
        session.answer(3)
        session.next()
    portrait = session.finish()
    assert [r.methodology_id for r in portrait.results] == [m.id for m in get_methodologies()]
    assert all(r.status == ResultStatus.OK for r in portrait.results)


def test_every_methodology_present_even_if_nothing_answered():
    portrait = SurveySession(get_methodologies()).finish()
    assert len(portrait.results) == 20
    assert all(r.status == ResultStatus.MISSING for r in portrait.results)
