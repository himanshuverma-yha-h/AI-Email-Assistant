import json
from datetime import datetime
from pathlib import Path


LOG_FILE = Path("data/action_audit_log.json")


def log_action(
    tool_name,
    arguments,
    success,
    message
):

    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool_name": tool_name,
        "arguments": arguments,
        "success": success,
        "message": message
    }

    logs = []

    if LOG_FILE.exists():

        try:

            with open(
                LOG_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                logs = json.load(file)

        except (
            json.JSONDecodeError,
            OSError
        ):

            logs = []

    logs.append(log_entry)

    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            logs,
            file,
            indent=4,
            ensure_ascii=False
        )