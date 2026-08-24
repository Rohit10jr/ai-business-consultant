# practice/

The durable practice profile. Everything `/setup` learns about how this practice works,
and nothing about any specific client.

| File | Writer | Tracked |
|---|---|---|
| `domains.md` | `/setup` | yes |
| `frameworks.md` | `/setup` | yes |
| `tracker.csv` | `/outcome` | **no — gitignored, holds real client names** |

`/setup` builds the two markdown files from the practice's own material in
`documents/practice/` (CV, past engagement summaries, methodology notes). That directory is
gitignored because past engagements name past clients.

`tracker.csv` is created by `/outcome` (phase 5). Expected columns, so nothing else has to
guess: `date, client, finding, recommendation, outcome, pushback, notes`. The guard in
`tools/check_no_client_data.py` fails if it is ever staged.
