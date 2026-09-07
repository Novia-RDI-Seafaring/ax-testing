# AX heuristics

The agent analog of Nielsen's usability heuristics. Use these to classify a
friction report and to design agent-facing surfaces. The cardinal failure is a
surface that lies: a human cross-checks a tool against the world, an agent
trusts the contract, so false confidence is the worst defect.

| id | Heuristic | A surface honors it when… |
| --- | --- | --- |
| `contract_truth` | **Contract truth** | The skill, the tool list, the command output, and any verdict describe the same reality. Nothing claims something false. |
| `pure_machine_output` | **Pure machine output** | `stdout` is parseable. Logs, progress, and chatter go to `stderr`. Errors are structured objects with a code and a hint, never a raw traceback. |
| `single_round_trip` | **Single round-trip sufficiency** | A result carries what the agent needs to act *and* to cite, without a follow-up call. |
| `honest_verdicts` | **Honest verdicts** | A check or probe fails only when the real operation would fail. No crying wolf. |
| `discoverability` | **Discoverability from the skill alone** | An agent reading only the skill can find the capability. A real tool the skill omits does not exist, as far as the agent is concerned. |
| `self_correcting_errors` | **Self-correcting, legible errors** | The tool repairs bad input where it can, and explains what to do when it cannot. |
| `affordance_completeness` | **Affordance completeness** | Every operation an agent reasonably needs is a first-class callable — a command, tool, or endpoint — not something it must assemble by probing, scraping, or reverse-engineering. The diagnostic tell of a violation: the agent had to write glue code to obtain something the tool should expose directly. The workaround is the evidence. |
| `other` | **Other** | Friction that does not fit the above. Describe it in `actual`. |

Severity ranks by blast radius:

- `critical` — silently produced a wrong result the agent could not detect.
- `high` — told the agent something false (missing capability, false verdict).
- `medium` — broke a parser or forced a fragile workaround.
- `low` — extra friction or a missing convenience.
