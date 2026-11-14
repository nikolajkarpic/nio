---
slug: 2026-11-14-short-lived-drivers
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10]  # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-14-short-lived-drivers` checks all of this. -->
# Run each gate or epic with a short-lived driver, and wait for long work by completion notice

## Summary
Implementing a feature takes about 8 hours and most of its tokens go to orchestration: on 2026-11-08 the main sessions
and their long-lived driver agents were about 76% of the estimated cost, because every turn re-reads everything the
effort has done so far, and about 90 sleep loops each re-read a context of up to 432k tokens. This makes each gate or
epic run in a fresh driver that starts from a short brief and ends with a short summary, keeps the main session to
routing, and has the implement and jury skills wait for long commands and subagents by completion notice instead of
polling, so an effort costs fewer tokens and less time with no change to what is judged or built (#128, #85). [human]

## Actors and journeys
- **A-1 Human**: runs efforts with NIO and pays their time and tokens; wants a feature implemented in less time and with fewer tokens. [human]
- **A-2 Main session**: the agent session the human talks to; it routes the effort from unit to unit and relays what needs the human. [human]
- **A-3 Driver**: a fresh agent that runs one unit of work (one gate, or one epic with its tasks and its implementation jury) and then ends. [human]
- **A-4 Host**: the agent tool NIO runs on (Claude Code or another); it may or may not offer subagents, background runs and completion notifications; the repo names Claude Code and Codex, and only Claude Code's are known. [research: RF-7]

**UJ-1 One unit of work** (A-2, A-3) [derived: FR-1, FR-2, FR-3, FR-4, RF-4]
1. The main session runs `nio flow next` and sees the next gate or epic.
2. It starts a fresh driver with the brief `nio flow brief` prints for that unit.
3. The driver runs the unit, starting long commands and subagents in the background and waiting for each to finish.
4. The driver ends with its summary: what closed, what is open, the next command.
5. The main session relays what needs the human, or starts the next unit's driver.
- Misuse: the main session opens a pack, a juror output or a test log "just to check"; a driver keeps going into the next unit instead of ending; a driver waits with a sleep loop out of habit.
- Evidence: #128, #85 and its 2026-11-14 comment (transcripts of #123, #49, #122); RF-4.

**UJ-2 A unit that needs the human** (A-1, A-2, A-3) [derived: FR-4, RF-9]
1. A driver reaches something only the human may decide (a human-only disposition, a blocked task).
2. It ends with a summary naming that open item and the command to continue.
3. The main session asks the human, then starts a fresh driver for the rest of the unit.
- Misuse: the driver decides the human's item itself to avoid ending.
- Evidence: today the effort already waits for the human there (RF-9).

## User stories

### US-1 Each gate or epic runs in a fresh driver (P1) [human]
- **Why this priority:** one long-lived driver was 29% of a day's cost at a 432k average context; restarting per unit is the largest saving measured (#128).
- **Independent test:** run an effort through two gates; each gate's work is done by a driver that started from a brief, not from the previous gate's context.

- **AC-1** (FR-1, FR-6) Given an effort at the spec, plan or tasks gate on a host with subagents, when the main session follows the jury skill, then the gate is run by a newly started driver, and that driver ends once the gate is closed or handed back. [human]
  Observable: the jury skill tells the main session to start a fresh driver per gate and the driver to end after its summary; in a run transcript, the gate's driver has no turn from an earlier gate. Level: e2e.
- **AC-2** (FR-2, FR-6) Given an effort implementing an epic on a host with subagents, when the main session follows the implement skill, then fresh drivers run that epic's tasks and its implementation jury one after another (a new one after each hand-back), and the next epic gets another fresh driver. [human]
  Observable: the implement skill says a driver covers one epic's tasks and its implementation jury and a resumed epic gets a fresh driver; in a run transcript, no driver works on two epics, and two epics have at least two drivers. Level: e2e.
- **AC-3** (FR-3) Given a unit about to start, when the main session starts its driver, then the driver's first input is the brief `nio flow brief` prints for the effort, and nothing from earlier units' drivers. [human]
  Observable: the skills tell the main session to start the driver from `nio flow brief <slug>` alone; in a run transcript the driver's first input holds no text written by an earlier driver, no earlier finding outside the brief and no juror output. Level: e2e.
- **AC-4** (FR-4) Given a driver that finished its unit, when it ends, then its last message says what closed, what is open and the next command, in at most 15 lines (NFR-1). [human]
  Observable: the skills give the summary's three parts and the 15-line limit; a run transcript's driver ends with a message holding all three in at most 15 non-empty lines. Level: e2e.
- **AC-5** (FR-11) Given a driver that reaches a human-only decision or a blocked task, when it cannot go on, then it ends with a summary naming the open item and the command to continue, and makes no decision that is the human's. [derived: FR-4, RF-9]
  Observable: the skills tell the driver to hand back with the open item; the ledger or task line shows no `--by human` disposition by the driver. Level: e2e.
- **AC-6** (FR-12) Given a driver already running for an effort, when the main session is asked to continue that effort, then it starts no second driver for it. [derived: FR-12]
  Observable: the skills tell the main session to start a driver only once the previous one has ended; a run transcript shows at most one driver per effort at a time; the skills say a driver that ended without a summary counts as ended and the main session goes on from `nio flow brief` alone. Level: e2e.

### US-2 The main session only routes (P1) [human]
- **Why this priority:** the main sessions ran 570 and 496 turns at 290k and 261k average context; reading packs and logs is what grows them (#128).
- **Independent test:** run a gate; the main session's transcript holds no read of a pack, juror output or test log.

- **AC-7** (FR-5, FR-15) Given an effort in progress on a host with subagents, when the main session routes it, then it reads no pack, juror output or test log itself, only the drivers' summaries and `nio flow` output. [human]
  Observable: the implement and jury skills say so; a run transcript's main session has no tool call reading a file under `.nio/runs/` or a test log. Level: e2e.
- **AC-8** (FR-5, FR-11) Given a driver's summary names an item for the human, when the main session relays it, then it does so from the summary alone. [derived: FR-4, FR-5]
  Observable: in a run transcript, the main session's message to the human follows the summary with no file read between them. Level: e2e.

### US-3 Long work is waited on by completion notice, never a sleep loop (P1) [human]
- **Why this priority:** about 90 wait loops on 2026-11-08 each re-read up to 432k tokens of context (#85 comment).
- **Independent test:** run a gate that runs `nio jury evidence`; the transcript shows one background start and one wake-up on completion, with no sleep or until loop.

- **AC-9** (FR-7, FR-8) Given a host with background runs and completion notifications, when a driver or the main session starts a long command or a subagent, then it starts it in the background and next acts on its completion notice. [human]
  Observable: the implement and jury skills say so up front; a run transcript has no `sleep` or `until` command and no status check between the start and the notice. Level: e2e.
- **AC-10** (FR-9) Given a host with no completion notifications, or one whose notices are unknown, when a long command is started, then the agent waits blocking with a 10-minute timeout, and does not poll. [human]
  Observable: the skills give this rule for such hosts, with the 10-minute timeout; the skill text holds no instruction to check at an interval, and its only check is the one after a timed-out wait (AC-11). Level: unit.
- **AC-11** (FR-10) Given a blocking wait that reached its timeout, when the command has not finished, then the agent checks once and waits again, and after the third wait that times out the driver ends with a summary naming the unfinished command as still running and how to continue. [derived: FR-10]
  Observable: the skills say: one check after each timeout, at most three waits in all, then the hand-back; no fourth wait. Level: unit.
- **AC-12** (FR-8) Given `nio flow green` started in the background that refuses (exits non-zero with a refusal text), when its completion notice arrives, then the driver goes to the implement skill's "On a refusal" step (step 3) with that refusal text. [human]
  Observable: in a run transcript, after the refused background `nio flow green` the driver starts a fresh worker for that phase and gives it the refusal text exactly as `nio flow green` printed it. Level: e2e.

### US-4 The skills stay host-neutral (P2) [human]
- **Why this priority:** NIO's skills must work on any agent host; the driver must not depend on one tool, but it comes after the savings themselves.
- **Independent test:** read the implement and jury skills; the driver and wait rules are plain instructions, with the Claude Code subagent named only as an option.

- **AC-13** (FR-7) Given the implement and jury skills, when read, then the driver and waiting rules are written as host-neutral instructions, and the Claude Code subagent appears only as an optional way to run a driver. [human]
  Observable: each skill holds the rules; the only Claude-specific mention is marked optional. Level: unit.
- **AC-14** (FR-13) Given a host without subagents, when an effort reaches a unit, then the main session runs the unit itself from the same brief, and does not stop for the human to start a session. [derived: FR-13]
  Observable: each skill has a step for hosts without subagents saying the main session runs the unit from `nio flow brief`; no step there asks the human for a fresh session. Level: unit.
- **AC-15** (FR-14) Given an effort at any stage, when `nio flow brief <slug>` runs, then it prints the stage, the open tasks, the open findings of the current gate, the next command and the skill, in at most 80 lines, and nothing it did not read from saved state. [derived: FR-14, NFR-2]
  Observable: on a fixture effort at a gate with two open findings and at implementing with two open tasks, the output names both findings, both tasks, the `nio flow next` command and skill, and has at most 80 lines; a second run on unchanged files prints the same. Level: unit.
- **AC-17** (FR-14) Given an effort whose open tasks and findings do not fit in 80 lines, when `nio flow brief <slug>` runs, then it prints how many there are, the first ones that fit, and the command that lists the rest, in at most 80 lines (NFR-2). [human]
  Observable: on a fixture effort with 100 open findings the output has at most 80 lines, gives the count 100, lists findings in ledger order from the first, and names the command that lists all of them. Level: unit.
- **AC-18** (FR-14) Given a slug with no effort under `.nio/specs/`, when `nio flow brief <slug>` runs, then it prints an error naming the slug and exits with code 1. [human]
  Observable: `nio flow brief no-such-slug` prints `error: no effort no-such-slug` to stderr and exits 1, with nothing on stdout. Level: unit.
- **AC-19** (FR-16) Given a host with no completion notifications and no blocking wait with a timeout, when a driver must run a long command, then it ends with a summary naming that command as open and how to continue, and the main session takes it to the human. [human]
  Observable: the skills give this rule for such hosts; no step tells the agent to run a long command in the foreground there. Level: unit.
- **AC-20** (FR-17, FR-14) Given a long command a driver started that is still running, when `nio flow brief <slug>` runs, then it prints `running: <command>, started <time>`, and once the command has ended it no longer does. [human]
  Observable: on a fixture effort with a running command recorded, the brief holds that line with the command and start time; after the command ends, a second brief has no `running:` line; the skills tell a driver whose brief shows `running:` to wait on that run, not start the command again. Level: unit.
- **AC-16** (FR-15) Given the implement and jury skills, when read, then each step FR-15 lists is a driver's step, and the main session's own steps name only `nio flow next`, `nio flow brief`, starting a driver and relaying its summary. [derived: FR-5, RF-10]
  Observable: each listed step sits under the driver's part of its skill; the main session's part names no pack, juror output, `nio jury evidence` or `nio flow red`/`green` output. Level: unit.

## Functional requirements
- **FR-1** WHERE the host has subagents, WHEN an effort reaches the spec, plan or tasks gate THE SYSTEM SHALL have that gate run by a newly started driver. [human]
- **FR-2** WHERE the host has subagents, WHEN an effort starts implementing an epic THE SYSTEM SHALL have newly started drivers, one after another (a new one after each hand-back), run that epic's tasks and its implementation jury. [human]
- **FR-3** WHEN a driver starts THE SYSTEM SHALL give it the brief `nio flow brief` prints for its effort, and no free-text note from an earlier driver. [human]
- **FR-4** WHEN a driver finishes its unit THE SYSTEM SHALL end it with a summary of what closed, what is open and the next command. [human]
- **FR-5** WHERE the host has subagents THE SYSTEM SHALL keep the main session to routing: it never reads packs, juror outputs or test logs itself. [human]
- **FR-6** WHERE the host has subagents, WHEN a driver has given its summary THE SYSTEM SHALL end that driver, and the next unit, or the rest of a unit resumed after a hand-back, SHALL get a new one. [human]
- **FR-7** THE SYSTEM SHALL state the driver and waiting rules in the implement and jury skills as host-neutral instructions, naming the Claude Code subagent only as an optional way to run a driver. [human]
- **FR-8** WHEN a driver or the main session starts a long command (Glossary) or a subagent on a host with completion notifications THE SYSTEM SHALL start it in the background and wait for its completion notice, never with a sleep loop or polling. [human]
- **FR-9** IF the host has no completion notifications, or it is unknown whether it has them, THEN THE SYSTEM SHALL wait for a long command with a blocking wait with a 10-minute timeout, never a poll (the one check after a timed-out wait, FR-10, is not a poll). [human]
- **FR-10** IF a blocking wait reaches its timeout before the command finishes THEN THE SYSTEM SHALL check once whether it finished and, if not, wait again, and after the third wait that times out end the driver with a summary naming the unfinished command as still running and how to continue, so the next driver waits on that run instead of starting it again (FR-17). [human]
- **FR-11** IF a driver reaches a decision that only the human may make, or a blocked task THEN THE SYSTEM SHALL end the driver with a summary naming that item and the command to continue. [derived: FR-4, RF-9]
- **FR-12** WHILE a driver is running for an effort THE SYSTEM SHALL start no second driver for that effort: the main session starts a unit's driver only once the previous one has ended; a driver that ended without a summary counts as ended, and the main session goes on from `nio flow brief` alone. [agent]
- **FR-13** IF the host has no subagents THEN THE SYSTEM SHALL have the main session run the unit itself from the same brief, without stopping for the human. [human]
- **FR-14** WHEN `nio flow brief <slug>` runs THE SYSTEM SHALL print the effort's brief from saved state alone: its stage, its open tasks and the open findings of its current gate, the next command and the skill to follow; when the open tasks and findings do not fit within NFR-2, it prints their counts, the first ones that fit and the command that lists the rest; for a slug with no effort it prints an error and exits non-zero; while a long command is recorded as running it prints `running: <command>, started <time>`. [human]
- **FR-15** WHERE the host has subagents THE SYSTEM SHALL have the driver, not the main session, do each step that reads or writes a juror output, a pack or test output: building escalation and fix-check pack copies, disposing of findings and fixing the artefact, running `nio jury evidence`, handing a worker the `nio flow red` output or a refusal's text, saving a `blocked` handoff, and reading what `nio flow green` prints. [derived: FR-5, RF-10]
- **FR-16** IF the host has no completion notifications and no blocking wait with a timeout THEN THE SYSTEM SHALL have the driver not run a long command, and end with a summary naming that command as open and how to continue, for the main session to take to the human. [human]
- **FR-17** WHEN a driver starts a long command THE SYSTEM SHALL record it as running in saved state, with the command and its start time, and clear that record when the command ends, so a later driver whose brief shows it running waits on it instead of starting it again. [human]

## Rules
### State table: driver (start: briefed; final: ended)
| State | brief given | unit closed | human item or blocked task | wait timed out | Src |
| --- | --- | --- | --- | --- | --- |
| briefed | → running | reject: nothing has run | reject: nothing has run | reject: nothing is waiting | [derived: FR-3, FR-4] |
| running | ignore | → ended | → ended | → ended | [derived: FR-4, FR-10, FR-16, RF-9] |
| ended | reject: the next unit, or a unit resumed after a hand-back, gets a new driver | ignore | ignore | ignore | [derived: FR-6, FR-12] |

`wait timed out` means the third timed-out wait (FR-10). Each move to `ended` gives the summary (FR-4, FR-10, FR-11). [derived: FR-4, FR-10, RF-9]

### Decision table: how to wait for a long command
| completion notices (yes, no) | blocking wait with timeout (yes, no) | → | Src |
| --- | --- | --- | --- |
| yes | - | start in the background, act on the notice | [human] |
| no | yes | a blocking wait with a 10-minute timeout, at most three | [human] |
| no | no | end the driver with a summary naming the command as open, for the human (FR-16) | [human] |

A host whose completion notices are unknown counts as `no` (FR-9). [derived: FR-9, RF-7]

## Key entities
- **Brief**: what a driver starts from, printed by `nio flow brief` from saved state: the stage, the open tasks and findings, the next command and the skill to follow. [human]
- **Summary**: what a driver ends with: what closed, what is open, the next command. [human]
- **Unit of work**: one gate, or one epic with its tasks and its implementation jury. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL keep a driver's end summary to at most 15 lines. [human]
- **NFR-2** THE SYSTEM SHALL keep a brief to at most 80 lines. [human]

## Success criteria
- **SC-1** On an effort comparable to those of 2026-11-08, orchestration's share of the estimated cost is below the ~76% measured then. [agent]
- **SC-2** A full effort's transcripts hold no `sleep` or `until` wait loop. [agent]
- **SC-3** No driver's average context in such an effort exceeds the 432k measured for the #49 driver. [agent]

## Non-goals
- Capping jury rounds and the other two fixes (#129, #126); the spec 2026-11-14-jury-round-cap covers them. [human]
- Making the commands themselves faster (#72, #73). [human]
- Changing what jurors judge, what workers build, or any gate's verdict rules. [agent]
- Changing who may grant auto mode or decide a human-only disposition. [agent]

## Glossary
- **Driver**: a fresh agent that runs one unit of work and then ends. Never "orchestrator subagent".
- **Main session**: the session the human talks to; it only routes. Never "orchestrator" when a driver is meant.
- **Long command**: a `nio` command or suite run that can outlast the host's foreground limit, such as `nio flow green`, `nio jury evidence` or a suite run, and any subagent.

## Decisions
- A gate step is driven by `nio jury next`, and jurors write their own output, so a driver need not read juror outputs: D-261107-pdq4 (memory, 2026-11-07).
- Only the human grants or revokes auto mode; a driver never does: D-261108-txqj (memory, 2026-11-08).
- The unit is one gate (spec, plan, tasks) or one epic with its tasks and its implementation jury: grill Q1 (2026-11-14).
- `nio` generates the brief from saved state; the outgoing driver writes no note: grill Q2 (2026-11-14).
- On a host without subagents the main session runs the unit itself: grill Q3 (2026-11-14).
- One driver at a time is a main-session rule, not a lock; the full-auto driver claim (C-261108-mplt, accepted; its branch is not merged) is left to that branch, and FR-12 does not rely on it: an agent call on FR-12 in the grill log (2026-11-14).
- Wait 10 minutes, at most three waits, then hand back: grill Q5 (2026-11-14). The 15- and 80-line limits and the spec jury's fixes: grill Q4 (2026-11-14).
- The implement skill's few-second retry on `try again` is not a wait on a long command and stays (RF-11).
