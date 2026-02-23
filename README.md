# blackroad-idea-board

Idea capture, development, and prioritization board. Score = votes × priority.

## Usage

```bash
# Capture an idea
python idea_board.py capture "AI-powered PR review" \
  --description "Use local LLM to review PRs automatically" \
  --category tech --priority 4

# Develop with notes
python idea_board.py develop 1 "Could use Ollama + git diff"

# Vote up
python idea_board.py vote 1

# Move through stages
python idea_board.py status 1 exploring
python idea_board.py status 1 validating
python idea_board.py status 1 building

# See prioritized board
python idea_board.py prioritize --limit 10

# Daily review (3 random exploring ideas)
python idea_board.py daily-review

# Ship it!
python idea_board.py ship 1 --result "Deployed as br-review command"

# Archive old stale ideas
python idea_board.py archive-old --days 90

# List all
python idea_board.py list
python idea_board.py list --status exploring --category tech

# Show detail
python idea_board.py show 1
```

## Status Pipeline

`captured` → `exploring` → `validating` → `building` → `shipped` | `archived`

## Score Formula

`score = votes × priority (1–5)`

## Storage

SQLite at `~/.blackroad-personal/idea_board.db`.

## License

Proprietary — BlackRoad OS, Inc.
