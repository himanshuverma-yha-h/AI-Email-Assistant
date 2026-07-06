import asyncio

import streamlit as st
from fastmcp import Client

from app.agents.email_assistant_agent import EmailAssistantAgent
from app.services.audit_service import log_action


st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="centered"
)


def run_async(coroutine):

    return asyncio.run(coroutine)


async def run_agent(
    user_request,
    conversation_history,
    approved_actions=None
):

    client = Client("mcp_server.py")

    async with client:

        agent = EmailAssistantAgent(
            mcp_client=client,
            conversation_history=conversation_history
        )

        response = await agent.run(
            user_request=user_request,
            approved_actions=approved_actions
        )

        return response


async def execute_tool(
    tool_name,
    arguments
):

    client = Client("mcp_server.py")

    try:

        async with client:

            result = await client.call_tool(
                tool_name,
                arguments
            )

            return result.data

    except Exception as error:

        print("\nCONFIRMED TOOL EXECUTION ERROR")
        print("=" * 70)

        print(
            f"Tool: {tool_name}"
        )

        print(
            f"Arguments: {arguments}"
        )

        print(
            f"Error: {error}"
        )

        return {
            "success": False,
            "message": (
                "The email action could not "
                "be completed. Please try again."
            )
        }


def show_confirmation_details(
    tool_name,
    arguments
):

    if tool_name == "reply_to_gmail_email":

        st.write(
            "The assistant wants to send "
            "the following reply:"
        )

        st.text_area(
            "Reply",
            value=arguments.get(
                "reply_body",
                ""
            ),
            height=220,
            disabled=True
        )

        return


    if tool_name == "send_gmail_email":

        st.write(
            "**Send a new email**"
        )

        st.write(
            f"**To:** "
            f"{arguments.get('to', 'Unknown')}"
        )

        st.write(
            f"**Subject:** "
            f"{arguments.get('subject', 'No Subject')}"
        )

        st.text_area(
            "Email body",
            value=arguments.get(
                "body",
                ""
            ),
            height=220,
            disabled=True
        )

        return


    if tool_name == "archive_gmail_email":

        st.write(
            "The assistant wants to archive "
            "the selected email."
        )

        return


    if tool_name == "mark_as_read":

        st.write(
            "The assistant wants to mark "
            "the selected email as read."
        )

        return


    st.write(
        "The assistant wants to perform "
        "an email action."
    )


if "messages" not in st.session_state:

    st.session_state.messages = []


if "pending_action" not in st.session_state:

    st.session_state.pending_action = None


st.title(
    "📧 AI Email Assistant"
)

st.caption(
    "Search, analyze and manage your Gmail "
    "using natural language."
)


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


user_request = st.chat_input(
    "Ask me about your emails..."
)


if user_request:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_request
        }
    )


    with st.spinner(
        "Working on your request..."
    ):

        response = run_async(
            run_agent(
                user_request=user_request,
                conversation_history=(
                    st.session_state.messages
                )
            )
        )


    if (
        isinstance(response, dict)
        and response.get("status")
        == "confirmation_required"
    ):

        st.session_state.pending_action = {
            "user_request": user_request,
            "tool_name": response["tool_name"],
            "arguments": response["arguments"]
        }

        st.rerun()


    else:

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        st.rerun()


if st.session_state.pending_action:

    pending = st.session_state.pending_action

    st.divider()

    st.subheader(
        "Confirmation Required"
    )

    st.warning(
        "This action will modify your Gmail account."
    )


    show_confirmation_details(
        tool_name=pending["tool_name"],
        arguments=pending["arguments"]
    )


    col1, col2 = st.columns(2)


    with col1:

        button_labels = {
            "reply_to_gmail_email": "Send Reply",
            "send_gmail_email": "Send Email",
            "archive_gmail_email": "Archive Email",
            "mark_as_read": "Mark as Read"
        }


        confirm_button_label = button_labels.get(
            pending["tool_name"],
            "Confirm Action"
        )


        if st.button(
            confirm_button_label,
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "Executing approved action..."
            ):

                result = run_async(
                    execute_tool(
                        tool_name=pending["tool_name"],
                        arguments=pending["arguments"]
                    )
                )


            if (
                isinstance(result, dict)
                and result.get("success")
            ):

                response = result.get(
                    "message",
                    "Action completed successfully."
                )

            else:

                if isinstance(
                    result,
                    dict
                ):

                    response = result.get(
                        "message",
                        "The action could not be completed."
                    )

                else:

                    response = (
                        "The action could not be completed."
                    )


            log_action(
                tool_name=pending["tool_name"],
                arguments=pending["arguments"],
                success=(
                    isinstance(result, dict)
                    and result.get(
                        "success",
                        False
                    )
                ),
                message=response
            )


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )


            st.session_state.pending_action = None

            st.rerun()


    with col2:

        if st.button(
            "Cancel",
            use_container_width=True
        ):

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Action cancelled."
                }
            )

            st.session_state.pending_action = None

            st.rerun()