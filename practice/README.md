# practice/

The durable practice profile. Everything `/setup` learns about how this practice works,
and nothing about any specific client.

| File | Writer | Tracked |
|---|---|---|
| `domains.md` | `/setup` | yes |
| `frameworks.md` | `/setup` | yes |
| `tracker.csv` | `/outcome` | **no — gitignored, holds real client names** |

`tracker.csv` is created by `/outcome` (phase 5). Expected columns, so nothing else has to
guess: `date, client, finding, recommendation, outcome, pushback, notes`. The guard in
`tools/check_no_client_data.py` fails if it is ever staged.
