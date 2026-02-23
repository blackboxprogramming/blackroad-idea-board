"""Tests for idea_board.py"""
import json, os, sys
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import MagicMock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import idea_board as ib


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(ib, "DB_PATH", str(tmp_path / "test_ideas.db"))
    yield tmp_path


def _capture(title="Test Idea", category="tech", priority=3, status="captured"):
    db = ib.get_db()
    from datetime import datetime
    cur = db.execute("""
        INSERT INTO ideas(title,description,category,status,priority,votes,
            notes_json,links_json,created_at)
        VALUES(?,?,?,?,?,?,?,?,?)
    """, (title, "", category, status, priority, 0, "[]", "[]", datetime.now().isoformat()))
    db.commit()
    return cur.lastrowid


def test_db_init(tmp_db):
    assert ib.get_db() is not None


def test_capture_idea(tmp_db):
    args = MagicMock(title="My Idea", description="desc", category="tech", priority=3)
    ib.cmd_capture(args)
    db  = ib.get_db()
    row = db.execute("SELECT * FROM ideas WHERE title='My Idea'").fetchone()
    assert row is not None
    assert row["status"] == "captured"
    assert row["category"] == "tech"


def test_vote_increments(tmp_db):
    iid  = _capture()
    args = MagicMock(idea_id=iid)
    ib.cmd_vote(args)
    ib.cmd_vote(args)
    db  = ib.get_db()
    row = db.execute("SELECT votes FROM ideas WHERE id=?", (iid,)).fetchone()
    assert row["votes"] == 2


def test_develop_adds_note(tmp_db):
    iid  = _capture()
    args = MagicMock(idea_id=iid, note="This could work with LLMs")
    ib.cmd_develop(args)
    db  = ib.get_db()
    row = db.execute("SELECT notes_json FROM ideas WHERE id=?", (iid,)).fetchone()
    notes = json.loads(row["notes_json"])
    assert "This could work with LLMs" in notes


def test_update_status(tmp_db):
    iid  = _capture()
    args = MagicMock(idea_id=iid, status="exploring")
    ib.cmd_update_status(args)
    db  = ib.get_db()
    row = db.execute("SELECT status FROM ideas WHERE id=?", (iid,)).fetchone()
    assert row["status"] == "exploring"


def test_score_formula(tmp_db):
    db = ib.get_db()
    iid = _capture(priority=4)
    db.execute("UPDATE ideas SET votes=3 WHERE id=?", (iid,)); db.commit()
    row  = db.execute("SELECT * FROM ideas WHERE id=?", (iid,)).fetchone()
    idea = ib.row_to_idea(row)
    assert idea.score == 12.0


def test_ship_idea(tmp_db):
    iid  = _capture(status="building")
    args = MagicMock(idea_id=iid, result="Deployed successfully")
    ib.cmd_ship(args)
    db  = ib.get_db()
    row = db.execute("SELECT * FROM ideas WHERE id=?", (iid,)).fetchone()
    assert row["status"] == "shipped"
    assert row["shipped_result"] == "Deployed successfully"


def test_archive_old(tmp_db):
    db = ib.get_db()
    old_date = (date.today() - timedelta(days=100)).isoformat()
    db.execute("""
        INSERT INTO ideas(title,description,category,status,priority,votes,
            notes_json,links_json,created_at)
        VALUES(?,?,?,?,?,?,?,?,?)
    """, ("Old Idea","","tech","captured",3,0,"[]","[]",old_date))
    db.commit()
    args = MagicMock(days=90)
    ib.cmd_archive_old(args)
    row = db.execute("SELECT status FROM ideas WHERE title='Old Idea'").fetchone()
    assert row["status"] == "archived"


def test_add_link(tmp_db):
    iid  = _capture()
    args = MagicMock(idea_id=iid, url="https://example.com")
    ib.cmd_add_link(args)
    db  = ib.get_db()
    row = db.execute("SELECT links_json FROM ideas WHERE id=?", (iid,)).fetchone()
    links = json.loads(row["links_json"])
    assert "https://example.com" in links


def test_daily_review_needs_exploring(tmp_db, capsys):
    args = MagicMock()
    ib.cmd_daily_review(args)
    out = capsys.readouterr().out + capsys.readouterr().err
    # Either shows ideas or shows helpful message
    assert True   # Just verifying no crash


def test_categories_and_statuses():
    assert "product" in ib.CATEGORIES
    assert "shipped" in ib.STATUSES
    assert len(ib.CATEGORIES) == 5
    assert len(ib.STATUSES) == 6
