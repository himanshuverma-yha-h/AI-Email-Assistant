from app.services.agent_service import (
    choose_next_action,
    generate_agent_response
)


class EmailAssistantAgent:

    def __init__(
        self,
        mcp_client,
        conversation_history=None
    ):

        self.mcp_client = mcp_client

        self.max_steps = 8

        self.action_tools = {
            "mark_as_read",
            "archive_gmail_email",
            "send_gmail_email",
            "reply_to_gmail_email"
        }

        if conversation_history is None:

            conversation_history = []

        self.conversation_history = (
            conversation_history
        )


    async def run(
        self,
        user_request,
        approved_actions=None
    ):

        if approved_actions is None:

            approved_actions = []

        try:

            tools = await self.mcp_client.list_tools()

        except Exception as error:

            print("\nMCP TOOL LIST ERROR")
            print("=" * 70)
            print(error)

            return (
                "I could not connect to the "
                "email tools. Please try again."
            )


        available_tool_names = {
            tool.name
            for tool in tools
        }


        history = []
        executed_calls = set()

        for step in range(
            1,
            self.max_steps + 1
        ):

            print("\nAGENT STEP")
            print("=" * 70)

            print(
                f"Step : {step}"
            )


            try:

                decision = choose_next_action(
                    user_request=user_request,
                    tools=tools,
                    history=history,
                    conversation_history=(
                        self.conversation_history
                    )
                )

            except Exception as error:

                print("\nAGENT REASONING ERROR")
                print("=" * 70)
                print(error)

                return (
                    "I could not understand how to "
                    "complete that email request."
                )


            print(
                f"Decision : {decision}"
            )


            action = decision.get(
                "action"
            )


            if action == "error":

                return decision.get(
                    "message",
                    "The request could not be processed."
                )


            if action == "finish":

                return generate_agent_response(
                    user_request=user_request,
                    tool_name="agent_history",
                    tool_result=history
                )


            if action == "tool":

                tool_name = decision.get(
                    "tool_name"
                )

                arguments = decision.get(
                    "arguments",
                    {}
                )


                if (
                    not tool_name
                    or tool_name
                    not in available_tool_names
                ):

                    return (
                        "The AI selected an unavailable "
                        "email action."
                    )


                if not isinstance(
                    arguments,
                    dict
                ):

                    return (
                        "The AI generated invalid "
                        "arguments for the email action."
                    )

                call_key = (
                    tool_name,
                    repr(
                        sorted(
                            arguments.items()
                        )
                    )
                )


                if call_key in executed_calls:

                    return generate_agent_response(
                        user_request=user_request,
                        tool_name="agent_history",
                        tool_result=history
                    )


                executed_calls.add(
                    call_key
                )

                print(
                    f"Tool      : {tool_name}"
                )

                print(
                    f"Arguments : {arguments}"
                )


                if (
                    tool_name in self.action_tools
                    and tool_name not in approved_actions
                ):

                    return {
                        "status": "confirmation_required",
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "message": (
                            "Confirmation required before "
                            f"executing {tool_name}."
                        )
                    }


                try:

                    result = (
                        await self.mcp_client.call_tool(
                            tool_name,
                            arguments
                        )
                    )

                except Exception as error:

                    print("\nMCP TOOL EXECUTION ERROR")
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

                    return (
                        "I could not complete the email "
                        f"action '{tool_name}'. "
                        "Please try again."
                    )


                tool_result = result.data


                history.append(
                    {
                        "step": step,
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "success": True,
                        "result": tool_result
                    }
                )


        return generate_agent_response(
            user_request=user_request,
            tool_name="agent_history",
            tool_result=history
        )