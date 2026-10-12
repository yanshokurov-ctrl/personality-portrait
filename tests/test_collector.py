import json

import pytest

from app.collector.collector import collect
from app.contracts import Answer, ResultStatus
from app.methodologies.stubs import StubMethodology
from tests.fakes import CrashingMethodology


def full_answers(methodology, value=3):
    return {q.id: Answer(q.id, value) for q in methodology.get_questions()}


def test_one_result_per_methodology_in_order():
    methodologies = [StubMethodology(f"m0{i}", f"Методика {i}") for i in (3, 1, 2)]
    grouped = {m.id: full_answers(m) for m in methodologies}
    portrait = collect(methodologies, grouped, {})
    assert [r.methodology_id for r in portrait.results] == ["m03", "m01", "m02"]


def test_failed_methodology_marked_as_error():
    first, second = StubMethodology("m01", "Первая"), StubMethodology("m02", "Вторая")
    portrait = collect([first, second], {"m01": full_answers(first)}, {"m02": "нет вопросов"})
    assert portrait.results[0].status == ResultStatus.OK
    assert portrait.results[1].status == ResultStatus.ERROR
    assert "нет вопросов" in portrait.results[1].message


def test_methodology_without_answers_is_missing():
    portrait = collect([StubMethodology("m01", "Первая")], {}, {})
    assert portrait.results[0].status == ResultStatus.MISSING


def test_crash_in_one_methodology_does_not_affect_others():
    good, bad = StubMethodology("m01", "Хорошая"), CrashingMethodology("m02", "Сломанная")
    portrait = collect([good, bad], {"m01": full_answers(good), "m02": full_answers(bad)}, {})
    assert [r.status for r in portrait.results] == [ResultStatus.OK, ResultStatus.ERROR]


def test_duplicate_methodologies_rejected():
    with pytest.raises(ValueError):
        collect([StubMethodology("m01", "А"), StubMethodology("m01", "Б")], {}, {})


def test_portrait_serializes_to_json():
    methodology = StubMethodology("m01", "Первая")
    portrait = collect([methodology], {"m01": full_answers(methodology)}, {})
    data = json.loads(json.dumps(portrait.to_dict(), ensure_ascii=False))
    assert data["results"][0]["status"] == "ok"
    assert data["results"][0]["scales"][0]["level"] == "medium"
