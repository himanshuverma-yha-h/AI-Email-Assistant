# AI Email Assistant

An agentic AI-powered Gmail assistant that uses natural language to search, analyze, draft, and manage emails.

The system uses an MCP-style tool architecture where an AI reasoning agent dynamically selects email tools based on the user's request.

## Features

- Search Gmail using natural language
- Find recent and unread emails
- Retrieve complete email content
- Analyze emails using AI
- Generate email summaries
- Classify email priority and category
- Recommend actions for emails
- Generate AI-powered reply drafts
- Reply inside existing Gmail threads
- Send new emails
- Mark emails as read
- Archive emails
- Multi-turn conversation support
- Human confirmation before Gmail-modifying actions
- Audit logging for confirmed actions
- Streamlit chat interface

## Architecture

The application follows an agentic tool-based workflow:

```text
User Request
      |
      v
Streamlit Chat Interface
      |
      v
Email Assistant Agent
      |
      v
AI Reasoning Engine
      |
      v
MCP Tool Selection
      |
      +-------------------+
      |                   |
      v                   v
 Gmail Service        AI Service
      |                   |
      +---------+---------+
                |
                v
          Tool Result
                |
                v
        Agent Reasoning
                |
                v
        Final User Response

        The AI agent decides which tool should be executed and can perform multiple tool calls to complete a request.

For example:
Find my latest unread email and analyze it

The agent can perform the following workflow:
1. Search Gmail for unread emails
2. Retrieve the selected email content
3. Analyze the email using AI
4. Generate a final response
MCP Tools

The MCP server exposes tools for email retrieval, AI analysis, and Gmail actions.

* search_email
* get_email_content
* analyze_email_content
* draft_email_reply
* mark_as_read
* archive_gmail_email
* send_gmail_email
* reply_to_gmail_email

Safety and Human Confirmation

Actions that modify Gmail require explicit user confirmation.

Protected actions include:

* Sending an email
* Replying to an email
* Archiving an email
* Marking an email as read

The assistant prepares the action and displays the relevant details before execution.

The Gmail action is executed only after the user explicitly confirms it.

Confirmed actions are recorded in a local audit log.

Tech Stack

* Python
* FastMCP
* Model Context Protocol (MCP)
* Google Gemini API
* Gmail API
* Google OAuth 2.0
* Streamlit

Project Structure
AI-Email-Assistant/
├── app/
│   ├── agents/
│   │   ├── email_agent.py
│   │   └── email_assistant_agent.py
│   ├── auth/
│   │   └── gmail_auth.py
│   ├── config/
│   │   └── settings.py
│   ├── database/
│   │   └── database.py
│   ├── models/
│   │   ├── analysis.py
│   │   └── email.py
│   ├── prompts/
│   │   ├── email_prompt.py
│   │   └── reply_prompt.py
│   ├── services/
│   │   ├── agent_service.py
│   │   ├── ai_service.py
│   │   ├── audit_service.py
│   │   ├── database_service.py
│   │   └── gmail_service.py
│   └── utils/
│       └── hash.py
├── mcp_client.py
├── mcp_server.py
├── streamlit_app.py
├── requirements.txt
├── README.md
└── .gitignore
