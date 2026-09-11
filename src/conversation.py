from src.database import DatabaseManager


class ConversationManager:

    def __init__(self, database):
        self.database = database

    # --------------------------------
    # CREATE SESSION
    # --------------------------------

    def create_session(
        self,
        title="New Chat"
    ):

        with self.database.connect() as connection:

            cursor = connection.execute(
                """
                INSERT INTO sessions
                (title)

                VALUES (?)
                """,
                (title,)
            )

            session_id = cursor.lastrowid

        return session_id

    # --------------------------------
    # CHECK SESSION
    # --------------------------------

    def session_exists(
        self,
        session_id
    ):

        with self.database.connect() as connection:

            row = connection.execute(
                """
                SELECT id
                FROM sessions
                WHERE id = ?
                """,
                (session_id,)
            ).fetchone()

        return row is not None

    # --------------------------------
    # SAVE MESSAGE
    # --------------------------------

    def add_message(
        self,
        session_id,
        role,
        content
    ):

        if role not in [
            "user",
            "assistant"
        ]:

            raise ValueError(
                "Invalid message role."
            )

        with self.database.connect() as connection:

            connection.execute(
                """
                INSERT INTO messages
                (
                    session_id,
                    role,
                    content
                )

                VALUES (?, ?, ?)
                """,
                (
                    session_id,
                    role,
                    content
                )
            )

            connection.execute(
                """
                UPDATE sessions

                SET updated_at =
                CURRENT_TIMESTAMP

                WHERE id = ?
                """,
                (session_id,)
            )

    # --------------------------------
    # GET CHAT HISTORY
    # --------------------------------

    def get_history(
        self,
        session_id
    ):

        with self.database.connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    role,
                    content,
                    created_at

                FROM messages

                WHERE session_id = ?

                ORDER BY id ASC
                """,
                (session_id,)
            ).fetchall()

        history = []

        for row in rows:

            history.append(
                {
                    "role": row["role"],
                    "content": row["content"],
                    "created_at": row["created_at"]
                }
            )

        return history

    # --------------------------------
    # BUILD LLM CONTEXT
    # --------------------------------

    def build_model_context(
        self,
        session_id,
        max_messages=12
    ):

        history = self.get_history(
            session_id
        )

        # Prevent unlimited context/token growth
        history = history[
            -max_messages:
        ]

        context = []

        for message in history:

            context.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )

        return context

    # --------------------------------
    # LIST ALL SESSIONS
    # --------------------------------

    def list_sessions(self):

        with self.database.connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    title,
                    created_at,
                    updated_at

                FROM sessions

                ORDER BY
                updated_at DESC,
                id DESC
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # --------------------------------
    # RENAME SESSION
    # --------------------------------

    def rename_session(
        self,
        session_id,
        title
    ):

        title = title.strip()

        if not title:
            title = "New Chat"

        with self.database.connect() as connection:

            connection.execute(
                """
                UPDATE sessions

                SET
                    title = ?,
                    updated_at = CURRENT_TIMESTAMP

                WHERE id = ?
                """,
                (
                    title,
                    session_id
                )
            )

    # --------------------------------
    # DELETE SESSION
    # --------------------------------

    def delete_session(
        self,
        session_id
    ):

        with self.database.connect() as connection:

            # Delete messages first
            connection.execute(
                """
                DELETE FROM messages

                WHERE session_id = ?
                """,
                (session_id,)
            )

            # Then delete session
            cursor = connection.execute(
                """
                DELETE FROM sessions

                WHERE id = ?
                """,
                (session_id,)
            )

        return cursor.rowcount > 0

    # --------------------------------
    # GET MESSAGE COUNT
    # --------------------------------

    def get_message_count(
        self,
        session_id
    ):

        with self.database.connect() as connection:

            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total

                FROM messages

                WHERE session_id = ?
                """,
                (session_id,)
            ).fetchone()

        return row["total"]

    # --------------------------------
    # AUTO TITLE SESSION
    # --------------------------------

    def auto_title_session(
        self,
        session_id,
        first_user_message
    ):

        title = first_user_message.strip()

        if not title:
            return

        if len(title) > 35:
            title = title[:32] + "..."

        self.rename_session(
            session_id,
            title
        )