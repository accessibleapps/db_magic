# Coordinated db_magic modernization

## Goal

Q approved the research recommendations with "using subagents, make this happen completely and entirely. Make it so!" Deliver the shared library and every direct consumer (QCast, QFeed, Chicken Nugget) through independent PRs, CI, and normal merges. No release or production deployment is part of this task.

## State

Owner worktree is db_magic-modernize on modernize/db-magic from fetched origin/master. Original checkout and research note are preserved. Three agents own separate consumer worktrees; root owns the library and publication. Library PR #3 is open. db_magic has no configured Actions workflows and the PR reports no checks. The actively authored tests/test_schema_upgrades.py passed all six cases under Python 3.8 with SQLAlchemy 2.0. Consumer PR CI must supply integrated build coverage.

## Decisions and why

- Delete magic.py and its relationship/FK generation, column shortcuts, model session/query/setup helpers, and partial typing protocols. Native SQLAlchemy owns these APIs.
- Keep TableNameMixin once for existing table naming. Entity extends it with native DeclarativeBase and integer id. Chicken Nugget retains its own db_id base using the naming mixin.
- Preserve existing database schemas, nullability, defaults, indexes, cascades, and column names. No data/schema renames.
- Support SQLAlchemy 2.0 and Python 3.8+, retaining the app runtime floor. Version 1.0 marks the API removal.
- Keep ordered SQLite upgrades with Session and SQLAlchemy Connection callback inputs. Runner owns each version's transaction and marker; callbacks must not commit. Reject missing upgrades before changes and reject newer schema versions.
- No compatibility API, replacement persistence facade, new CI workflow, or release machinery.
- Direct source/manifest edges establish the three consumers. The Accessible Apps coordination topology does not currently contain db_magic; do not expand that separate repository as a prerequisite for this authorized task.

## Surprises

QCast has independent open PRs for OPML and commit retry work; avoid inheriting or silently replacing them. Chicken Nugget has differing source/target event relationship columns requiring source-based preservation. QFeed's old lock predates owner migration fixes.

## Next step

Owner API is committed, published, and supplied to agents. Complete consumer migrations and pins, inspect diffs, review actual published PRs, follow CI and repair failures, then merge normally and clean task worktrees/branches. All consumers pin the published owner revision. Merge consumers with executable pins before the breaking owner default-branch change, so Chicken Nugget's old floating requirement is replaced before owner integration. Record PR numbers and terminal evidence here without commit IDs.

## Delivery checkpoint

Chicken Nugget PR #3 is merged after ordinary and protected CI passed on its repaired head. The existing master checkout contains the remote merge and preserves its pre-existing local note-move commit. Task worktree and local/remote branch removed. Review caught current-thread-only disconnect cleanup; native close_all_sessions restores the previous close-all contract without new infrastructure.

QFeed PR #4 has completed review and passed ordinary CI with 91 tests plus executable build; protected Python 3.10 interpreter build is still running. QCast PR #69 is under new-head CI after replacing an invalid relationship Mock fixture and completing ID-based saved-index worker ownership. Its review gate is complete, reusing unchanged coverage and reviewing only the repair delta. Separate QCast PR #68 remains open and unchanged.

No release, tag, or deployment has occurred. Finish current-head CI, merge each passing independent consumer, then merge owner PR #3, verify normal merge topology and consumer pins, integrate locally and clean remaining task worktrees/branches.

## Shared ID typing repair

QCast's repaired CI passes its runtime suite but Pyright reports five unnecessary-None-check errors in download_manager.py. The shared Entity declaration incorrectly typed transient IDs as always int. Correct the owner declaration to Optional[int], with nullable=False explicitly preserving the original database primary key. Do not remove valid transient-ID checks or weaken Pyright. Repin all consumers to the repaired owner; Chicken Nugget already merged its source migration, so its final pin needs an independent follow-up PR. Include this existing note update with the substantive owner correction.
