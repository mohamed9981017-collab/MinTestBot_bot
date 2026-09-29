# Job Hunter Bot

An RSS → Telegram bot that watches job feeds and posts new, keyword-matching
listings to a Telegram chat. No database required: delivered jobs are tracked in
a small JSON state file so nothing is posted twice.

## How it works

1. Fetch every configured RSS/Atom feed (`feedparser` + `requests`).
2. Normalise each entry (strip HTML, build a stable id).
3. Filter by include/exclude keywords (case-insensitive, word-boundary aware).
4. Drop anything already delivered (state file).
5. Send the rest to Telegram as HTML messages.

## Requirements

- Python 3.10+
- A Telegram bot token and a target chat id
- `pip install -r requirements.txt`

## Configuration

Copy `.env.example` to `.env` and fill it in, or export the variables directly:

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `TELEGRAM_TOKEN` | yes | – | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | yes | – | Chat/channel/user id to post to |
| `RSS_FEEDS` | one of | – | Comma/newline separated feed URLs |
| `RSS_FEEDS_FILE` | one of | – | Path to a file with one feed URL per line |
| `JOB_KEYWORDS` | no | empty | Include keywords; empty keeps everything |
| `EXCLUDE_KEYWORDS` | no | empty | Keywords that discard an entry |
| `POLL_INTERVAL` | no | `900` | Seconds between cycles in loop mode |
| `MAX_ITEMS_PER_RUN` | no | `20` | Cap on messages sent per cycle |
| `REQUEST_TIMEOUT` | no | `20` | HTTP timeout in seconds |
| `STATE_FILE` | no | `seen_jobs.json` | Path to the dedupe state file |
| `DRY_RUN` | no | `false` | Log matches without sending |

## Usage

```bash
# one cycle, then exit
python main.py --once

# preview matches without sending anything
python main.py --once --dry-run

# poll forever
python main.py
```

## Tests

```bash
pip install pytest
python -m pytest -q
```

The suite covers config parsing, feed parsing, keyword filtering, message
formatting and the dedupe store, plus an end-to-end cycle served by a real
local HTTP server that stands in for both the RSS feed and the Telegram API.

## Project layout

```
main.py              # CLI entrypoint (--once / loop / --dry-run)
jobhunter/
  config.py          # environment -> Config
  feeds.py           # fetch + parse RSS/Atom
  filters.py         # keyword include/exclude
  formatting.py      # Telegram HTML rendering
  store.py           # JSON dedupe store
  telegram.py        # Bot API client
  hunter.py          # the poll cycle
tests/               # unit + end-to-end tests
```
