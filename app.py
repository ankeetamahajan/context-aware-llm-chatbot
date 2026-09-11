from src.database import DatabaseManager
from src.conversation import ConversationManager
from src.chatbot import Chatbot


HELP_TEXT = """
Commands:

/new
    Start new conversation

/sessions
    Show saved conversations

/history
    Show current conversation

/resume <id>
    Resume old conversation

/exit
    Close chatbot

/help
    Show commands
""".strip()


def main():

    database = DatabaseManager()

    conversation = ConversationManager(
        database
    )

    chatbot = Chatbot()

    session_id = (
        conversation.create_session()
    )

    print(
        "\n"
        "=========================================="
    )

    print(
        " CONTEXT-AWARE LLM CHATBOT"
    )

    print(
        " WITH PERSISTENT MEMORY"
    )

    print(
        "=========================================="
    )

    print(
        f"\nCurrent Session ID: "
        f"{session_id}"
    )

    print(
        "\nType /help for commands."
    )

    while True:

        try:

            user_input = input(
                "\nYou: "
            ).strip()

            if not user_input:

                continue

            # ------------------------
            # EXIT
            # ------------------------

            if user_input == "/exit":

                print(
                    "\nConversation saved."
                )

                print(
                    "Goodbye!"
                )

                break

            # ------------------------
            # HELP
            # ------------------------

            if user_input == "/help":

                print(
                    "\n" + HELP_TEXT
                )

                continue

            # ------------------------
            # NEW SESSION
            # ------------------------

            if user_input == "/new":

                session_id = (
                    conversation
                    .create_session()
                )

                print(
                    "\nNew session created."
                )

                print(
                    "Session ID:",
                    session_id
                )

                continue

            # ------------------------
            # LIST SESSIONS
            # ------------------------

            if user_input == "/sessions":

                sessions = (
                    conversation
                    .list_sessions()
                )

                print(
                    "\nSaved Sessions:"
                )

                for session in sessions:

                    print(
                        f"ID: {session['id']} | "
                        f"Title: {session['title']} | "
                        f"Updated: "
                        f"{session['updated_at']}"
                    )

                continue

            # ------------------------
            # HISTORY
            # ------------------------

            if user_input == "/history":

                history = (
                    conversation
                    .get_history(
                        session_id
                    )
                )

                print(
                    "\nConversation History:"
                )

                for message in history:

                    print(
                        f"\n"
                        f"{message['role'].upper()}: "
                        f"{message['content']}"
                    )

                continue

            # ------------------------
            # RESUME
            # ------------------------

            if user_input.startswith(
                "/resume "
            ):

                try:

                    requested_id = int(
                        user_input
                        .split()[1]
                    )

                except Exception:

                    print(
                        "Usage: /resume <id>"
                    )

                    continue

                if (
                    conversation
                    .session_exists(
                        requested_id
                    )
                ):

                    session_id = (
                        requested_id
                    )

                    print(
                        "\nResumed session:",
                        session_id
                    )

                else:

                    print(
                        "\nSession not found."
                    )

                continue

            # ------------------------
            # NORMAL MESSAGE
            # ------------------------

            conversation.add_message(
                session_id,
                "user",
                user_input
            )

            # Load recent memory
            messages = (
                conversation
                .build_model_context(
                    session_id,
                    max_messages=12
                )
            )

            print(
                "\nAssistant is thinking..."
            )

            answer = chatbot.reply(
                messages
            )

            # Save assistant reply
            conversation.add_message(
                session_id,
                "assistant",
                answer
            )

            print(
                "\nAssistant:",
                answer
            )

        except KeyboardInterrupt:

            print(
                "\nConversation saved."
            )

            break

        except Exception as error:

            print(
                "\nERROR:",
                error
            )


if __name__ == "__main__":
    main()