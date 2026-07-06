import asyncio

from fastmcp import Client

from app.agents.email_assistant_agent import EmailAssistantAgent


client = Client("mcp_server.py")


async def main():

    async with client:

        agent = EmailAssistantAgent(client)

        print("\nAI EMAIL ASSISTANT")
        print("=" * 70)

        user_request = input(
            "\nWhat would you like me to do?\n\n> "
        )

        response = await agent.run(
            user_request
        )

        if (
            isinstance(response, dict)
            and response.get("status")
            == "confirmation_required"
        ):

            print("\nCONFIRMATION REQUIRED")
            print("=" * 70)

            print(
                f"Action : {response['tool_name']}"
            )

            print(
                f"Arguments : {response['arguments']}"
            )

            confirmation = input(
                "\nAllow this action? (yes/no): "
            )

            if confirmation.lower() == "yes":

                response = await agent.run(
                    user_request,
                    approved_actions=[
                        response["tool_name"]
                    ]
                )

            else:

                response = "Action cancelled."

        print("\nASSISTANT RESPONSE")
        print("=" * 70)

        print(response)


if __name__ == "__main__":

    asyncio.run(main())