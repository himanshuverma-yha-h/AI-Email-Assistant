# AI Email Assistant

An agentic AI-powered Gmail assistant that uses natural language to search, analyze, summarize, draft, and manage emails.

The system uses a Model Context Protocol (MCP) tool architecture where an AI reasoning agent dynamically selects tools and performs multi-step email workflows based on the user's request.

## Features

- Search Gmail using natural language
- Find recent and unread emails
- Retrieve complete email content
- Analyze emails using Google Gemini
- Generate prioritized email digests
- Summarize daily emails
- Classify emails by priority and category
- Recommend actions for emails
- Cache AI email analysis using SQLite
- Generate AI-powered reply drafts
- Compose complete emails from informal user intent
- Reply inside existing Gmail threads
- Send new emails
- Mark emails as read
- Archive emails
- Multi-turn conversation support
- Resolve follow-up references such as "that email" or "the first one"
- Human confirmation before Gmail-modifying actions
- Display email context before confirming archive or mark-as-read actions
- Audit logging for confirmed Gmail actions
- Streamlit chat interface
- Timezone-aware handling of "today" using Asia/Kolkata

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
Gemini Reasoning Engine
      |
      v
MCP Tool Selection
      |
      +----------------------+----------------------+
      |                      |                      |
      v                      v                      v
 Gmail Service          AI Service          Database Service
      |                      |                      |
      v                      v                      v
 Gmail API              Gemini API               SQLite
      |                      |                      |
      +----------------------+----------------------+
                             |
                             v
                         Tool Result
                             |
                             v
                      Agent Reasoning
                             |
                  +----------+----------+
                  |                     |
                  v                     v
            Select Next Tool       Finish Request
                                        |
                                        v
                               Final User Response
```

The AI agent decides which MCP tool should be executed and can perform multiple tool calls to complete a request.

For deterministic operations such as timezone handling, timestamps, confirmation checks, database caching, and action validation, the application uses Python logic instead of relying on the language model.

## Example Agent Workflow

User request:

```text
Find my latest unread email and analyze it.
```

The agent can perform the following workflow:

```text
1. search_email
2. get_email_content
3. analyze_email_content
4. finish
```

For a daily email digest:

```text
Summarize my emails from today and show the most important ones first.
```

The workflow becomes:

```text
1. generate_email_digest
2. finish
```

The batch digest tool avoids repeatedly calling separate tools for every email.

## MCP Tools

The MCP server exposes the following tools:

### `search_email`

Searches Gmail using Gmail search syntax.

Examples:

```text
is:unread
from:google
subject:internship
newer_than:7d
```

### `get_email_content`

Retrieves the complete content of a Gmail message using its Gmail message ID.

### `analyze_email_content`

Uses Gemini to analyze an email and return:

- Summary
- Category
- Priority
- Recommended action

### `generate_email_digest`

Searches matching emails, reuses cached AI analysis when available, analyzes uncached emails, and returns emails ordered by priority.

Priority order:

```text
High
Medium
Low
```

### `draft_email_reply`

Generates a professional AI reply draft for an existing email.

This tool creates a draft only and does not send the email.

### `mark_as_read`

Marks a Gmail message as read.

Requires user confirmation before execution.

### `archive_gmail_email`

Archives a Gmail message.

Requires user confirmation before execution.

### `send_gmail_email`

Sends a new Gmail email.

The reasoning engine can convert an informal user instruction into a polished email subject and body before requesting confirmation.

### `reply_to_gmail_email`

Replies to an existing email inside the same Gmail conversation thread.

Requires user confirmation before execution.

## AI Reasoning Agent

The `EmailAssistantAgent` controls the multi-step agent loop.

For every user request, the agent:

1. Retrieves available MCP tools.
2. Sends the user request, available tools, previous tool history, and conversation history to the reasoning engine.
3. Receives a structured next-action decision.
4. Validates the selected tool and arguments.
5. Requests confirmation for Gmail-modifying actions.
6. Executes approved or read-only tools.
7. Stores tool results in the current action history.
8. Repeats the reasoning process until the request is complete or the maximum step limit is reached.

The agent uses a maximum step limit to reduce the risk of uncontrolled tool loops.

## Daily Email Digest

Daily digest requests use the `generate_email_digest` batch MCP tool.

The workflow is:

```text
Search Gmail
      |
      v
Retrieve Matching Emails
      |
      v
Check Gmail ID in SQLite
      |
      +----------------------+
      |                      |
      v                      v
Analysis Exists        Analysis Missing
      |                      |
      v                      v
Load Cached Analysis   Analyze with Gemini
      |                      |
      |                      v
      |                Save to SQLite
      |                      |
      +-----------+----------+
                  |
                  v
           Build Digest List
                  |
                  v
       Sort High -> Medium -> Low
                  |
                  v
          Return Email Digest
```

Each Gmail message is treated as a separate digest item.

The final response displays every returned email individually and preserves the priority ordering produced by the digest tool.

## SQLite Analysis Cache

The application uses SQLite to cache AI-generated email analysis.

Database file:

```text
data/emails.db
```

The `email_analysis` table stores:

- Gmail message ID
- Sender
- Subject
- Date
- Summary
- Category
- Priority
- Recommended action

The Gmail message ID is used as the primary key.

Before sending an email to Gemini for analysis, the application checks whether analysis already exists for that Gmail message ID.

If analysis exists:

```text
Load analysis from SQLite
```

If analysis does not exist:

```text
Analyze with Gemini
        |
        v
Save analysis to SQLite
```

This prevents repeated AI analysis of the same email and avoids duplicate analysis records.

The database caches AI analysis, not the complete Gmail email body.

## Timezone-Aware "Today" Handling

The application distinguishes between:

```text
today
```

and:

```text
last 24 hours
```

These are not treated as the same time range.

For requests containing "today", Python calculates midnight for the current calendar date using:

```text
Asia/Kolkata
```

The exact midnight time is converted to a Unix timestamp and enforced in the Gmail search query.

Example workflow:

```text
User asks for today's emails
        |
        v
Python detects "today"
        |
        v
Calculate 00:00 Asia/Kolkata
        |
        v
Convert to Unix timestamp
        |
        v
Override AI-generated date query
        |
        v
Search Gmail from exact local midnight
```

For requests asking for the last 24 hours, Gmail's `newer_than:1d` search syntax can be used.

This keeps deterministic date and timezone calculations in Python instead of depending on the language model.

## Gmail Integration

The application integrates with Gmail using the Gmail API.

The Gmail service supports:

- Searching messages
- Retrieving complete messages
- Parsing email headers
- Extracting plain-text email bodies
- Marking messages as read
- Archiving messages
- Sending new emails
- Replying inside existing Gmail threads

Email bodies are decoded from Gmail's URL-safe Base64 format.

Threaded replies use:

- Gmail thread ID
- `Message-ID`
- `In-Reply-To`
- `References`

This allows replies to remain inside the existing Gmail conversation thread.

## Gmail Authentication

The application uses Google OAuth 2.0.

The user provides a Google OAuth desktop application credential file:

```text
credentials.json
```

On the first Gmail authorization, the application opens the Google OAuth consent flow.

After successful authorization, Gmail access credentials are stored locally in:

```text
token.json
```

On future runs, the stored token is reused when valid.

Sensitive authentication files are excluded from Git using `.gitignore`.

## Gemini Integration

The application uses the Google Gemini API for:

- Agent reasoning
- MCP tool selection
- Email analysis
- Email summarization
- Priority classification
- Category classification
- Recommended actions
- Reply generation
- New email composition
- Final natural-language responses

The Gemini API key is loaded from an environment variable:

```text
GEMINI_API_KEY
```

The key is stored locally in:

```text
.env
```

The `.env` file is excluded from Git.

## Human Confirmation and Safety

Actions that modify Gmail require explicit user confirmation.

Protected actions include:

- Sending an email
- Replying to an email
- Archiving an email
- Marking an email as read

The assistant prepares the action and displays relevant details before execution.

For a new email, the confirmation interface displays:

- Recipient
- Subject
- Complete email body

For a reply, the complete reply body is displayed.

For archive and mark-as-read actions, email context such as sender, subject, and date is displayed.

The Gmail action is executed only after the user explicitly confirms it.

## Audit Logging

Confirmed Gmail actions are recorded in a local audit log:

```text
data/action_audit_log.json
```

Each audit record contains:

- Timestamp
- Tool name
- Tool arguments
- Success status
- Result message

The audit log is excluded from Git because it can contain Gmail-related metadata.

## Tech Stack

- Python
- FastMCP
- Model Context Protocol (MCP)
- Google Gemini API
- Gmail API
- Google OAuth 2.0
- SQLite
- Streamlit

## Project Structure

```text
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
├── data/
│   ├── emails.db
│   └── action_audit_log.json
├── mcp_client.py
├── mcp_server.py
├── streamlit_app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/himanshuverma-yha-h/AI-Email-Assistant.git
cd AI-Email-Assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

Activate it on Windows:

```text
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Configure Gmail OAuth

Create a Google Cloud project and enable the Gmail API.

Create OAuth 2.0 credentials for a Desktop application.

Download the OAuth credential file and place it in the project root as:

```text
credentials.json
```

The first Gmail request will start the Google OAuth authorization flow.

After authorization, the local Gmail token is stored as:

```text
token.json
```

### 6. Run the application

```bash
streamlit run streamlit_app.py
```

Open the local Streamlit URL shown in the terminal.

## Security

The following files are excluded from Git:

```text
.env
credentials.json
token.json
data/emails.db
data/action_audit_log.json
```

Never commit API keys, OAuth credentials, Gmail tokens, local email analysis databases, or Gmail action audit logs to a public repository.

## Example Requests

```text
Find my latest 3 unread emails.

Analyze my latest placement email.

Draft a reply to the first email.

Send an email to example@gmail.com telling them that I completed my project.

Mark that email as read.

Archive the second email.

Summarize my emails from today and show the most important ones first.

Summarize emails from the last 24 hours.
```

## Author

Himanshu Verma