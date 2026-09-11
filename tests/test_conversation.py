import pytest

import src.database as database_module
from src.database import DatabaseManager
from src.conversation import ConversationManager


@pytest.fixture
def manager(tmp_path, monkeypatch):

    test_database = (
        tmp_path / "test_chat_memory.db"
    )

    monkeypatch.setattr(
        database_module,
        "DATABASE_FILE",
        test_database
    )

    database = DatabaseManager()

    return ConversationManager(
        database
    )


def test_create_session(manager):

    session_id = (
        manager.create_session(
            "Test Chat"
        )
    )

    assert session_id == 1

    assert manager.session_exists(
        session_id
    )


def test_save_and_load_messages(manager):

    session_id = (
        manager.create_session()
    )

    manager.add_message(
        session_id,
        "user",
        "My name is Ankeeta."
    )

    manager.add_message(
        session_id,
        "assistant",
        "Hello Ankeeta."
    )

    history = manager.get_history(
        session_id
    )

    assert len(history) == 2

    assert (
        history[0]["role"]
        == "user"
    )

    assert (
        history[0]["content"]
        == "My name is Ankeeta."
    )

    assert (
        history[1]["role"]
        == "assistant"
    )


def test_context_limit(manager):

    session_id = (
        manager.create_session()
    )

    for number in range(20):

        role = (
            "user"
            if number % 2 == 0
            else "assistant"
        )

        manager.add_message(
            session_id,
            role,
            f"Message {number}"
        )

    context = (
        manager.build_model_context(
            session_id,
            max_messages=6
        )
    )

    assert len(context) == 6

    assert (
        context[0]["content"]
        == "Message 14"
    )

    assert (
        context[-1]["content"]
        == "Message 19"
    )


def test_rename_session(manager):

    session_id = (
        manager.create_session()
    )

    manager.rename_session(
        session_id,
        "Python Discussion"
    )

    sessions = (
        manager.list_sessions()
    )

    assert (
        sessions[0]["title"]
        == "Python Discussion"
    )


def test_message_count(manager):

    session_id = (
        manager.create_session()
    )

    manager.add_message(
        session_id,
        "user",
        "Hello"
    )

    manager.add_message(
        session_id,
        "assistant",
        "Hi"
    )

    assert (
        manager.get_message_count(
            session_id
        )
        == 2
    )


def test_delete_session(manager):

    session_id = (
        manager.create_session()
    )

    manager.add_message(
        session_id,
        "user",
        "Delete this conversation."
    )

    result = (
        manager.delete_session(
            session_id
        )
    )

    assert result is True

    assert not manager.session_exists(
        session_id
    )


def test_invalid_role(manager):

    session_id = (
        manager.create_session()
    )

    with pytest.raises(
        ValueError
    ):

        manager.add_message(
            session_id,
            "system",
            "Invalid"
        )