import streamlit as st

from src.database import DatabaseManager
from src.conversation import ConversationManager
from src.chatbot import Chatbot


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Context-Aware AI Assistant",
    page_icon="🧠",
    layout="wide"
)


# ==================================================
# INITIALIZE BACKEND
# ==================================================

@st.cache_resource
def get_database():
    return DatabaseManager()


@st.cache_resource
def get_chatbot():
    return Chatbot()


database = get_database()

conversation = ConversationManager(
    database
)

chatbot = get_chatbot()


# ==================================================
# SESSION STATE
# ==================================================

if "session_id" not in st.session_state:

    existing_sessions = (
        conversation.list_sessions()
    )

    # If previous sessions already exist,
    # open the latest one.
    if existing_sessions:

        st.session_state.session_id = (
            existing_sessions[0]["id"]
        )

    else:

        # Otherwise create the first chat.
        st.session_state.session_id = (
            conversation.create_session(
                "New Chat"
            )
        )


current_session = (
    st.session_state.session_id
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    # --------------------------------------------------
    # APP TITLE
    # --------------------------------------------------

    st.title(
        "🧠 AI Memory Chat"
    )

    st.caption(
        "Context-aware chatbot "
        "with persistent memory"
    )

    st.divider()


    # --------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        current_count = (
            conversation.get_message_count(
                current_session
            )
        )

        # Create a new session only if
        # the current session already contains messages.
        if current_count > 0:

            new_session = (
                conversation.create_session(
                    "New Chat"
                )
            )

            st.session_state.session_id = (
                new_session
            )

            st.rerun()

        else:

            st.info(
                "You are already in an empty new chat."
            )


    st.divider()


    # --------------------------------------------------
    # SAVED CONVERSATIONS
    # --------------------------------------------------

    st.subheader(
        "Saved Conversations"
    )

    sessions = (
        conversation.list_sessions()
    )

    if not sessions:

        st.caption(
            "No saved conversations yet."
        )

    else:

        for session in sessions:

            session_id = (
                session["id"]
            )

            title = (
                session["title"]
            )

            # Shorten long titles
            if len(title) > 28:

                title = (
                    title[:25]
                    + "..."
                )

            # Mark currently selected chat
            if (
                session_id
                == current_session
            ):

                button_text = (
                    f"▶️ {title}"
                )

            else:

                button_text = (
                    f"💬 {title}"
                )


            if st.button(
                button_text,
                key=f"session_{session_id}",
                use_container_width=True
            ):

                st.session_state.session_id = (
                    session_id
                )

                st.rerun()


    st.divider()


    # --------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------

    st.subheader(
        "System"
    )

    message_count = (
        conversation.get_message_count(
            current_session
        )
    )

    st.write(
        f"**Messages:** "
        f"{message_count}"
    )

    st.write(
        "**Memory:** ✅ Active"
    )

    st.write(
        "**Database:** SQLite"
    )

    st.write(
        "**LLM:** Hugging Face"
    )


    st.divider()


    # --------------------------------------------------
    # DELETE CURRENT CHAT
    # --------------------------------------------------

    if st.button(
        "🗑️ Delete Current Chat",
        use_container_width=True
    ):

        conversation.delete_session(
            current_session
        )

        remaining_sessions = (
            conversation.list_sessions()
        )

        # If another chat exists,
        # switch to the latest one.
        if remaining_sessions:

            st.session_state.session_id = (
                remaining_sessions[0]["id"]
            )

        else:

            # If all chats were deleted,
            # create one fresh empty session.
            st.session_state.session_id = (
                conversation.create_session(
                    "New Chat"
                )
            )

        st.rerun()


# ==================================================
# MAIN PAGE
# ==================================================

st.title(
    "🧠 Context-Aware LLM Chatbot"
)

st.caption(
    "Persistent Memory • "
    "Hugging Face • "
    "SQLite • "
    "Python • "
    "Streamlit"
)


# ==================================================
# LOAD CHAT HISTORY
# ==================================================

history = (
    conversation.get_history(
        current_session
    )
)


# ==================================================
# DISPLAY EXISTING MESSAGES
# ==================================================

for message in history:

    role = (
        message["role"]
    )

    content = (
        message["content"]
    )

    with st.chat_message(
        role
    ):

        st.markdown(
            content
        )


# ==================================================
# CHAT INPUT
# ==================================================

user_message = (
    st.chat_input(
        "Type your message..."
    )
)


# ==================================================
# PROCESS NEW MESSAGE
# ==================================================

if user_message:

    # --------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_message
        )


    # --------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------

    conversation.add_message(
        current_session,
        "user",
        user_message
    )


    # --------------------------------------------------
    # AUTO-TITLE NEW CHAT
    # --------------------------------------------------

    if len(history) == 0:

        conversation.auto_title_session(
            current_session,
            user_message
        )


    # --------------------------------------------------
    # BUILD LLM CONTEXT
    # --------------------------------------------------

    context = (
        conversation.build_model_context(
            current_session,
            max_messages=12
        )
    )


    # --------------------------------------------------
    # GENERATE ASSISTANT RESPONSE
    # --------------------------------------------------

    try:

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Thinking..."
            ):

                response = (
                    chatbot.reply(
                        context
                    )
                )

            st.markdown(
                response
            )


        # --------------------------------------------------
        # SAVE ASSISTANT RESPONSE
        # --------------------------------------------------

        conversation.add_message(
            current_session,
            "assistant",
            response
        )


        # Refresh:
        # - sidebar title
        # - message count
        # - conversation list
        st.rerun()


    except Exception as error:

        st.error(
            "LLM request failed."
        )

        st.code(
            str(error)
        )