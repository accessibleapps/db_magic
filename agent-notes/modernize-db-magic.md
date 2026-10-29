# Coordinated db_magic modernization

## Goal

Q approved the research recommendations with "using subagents, make this happen completely and entirely. Make it so!" Deliver the shared library and every direct consumer (QCast, QFeed, Chicken Nugget) through independent PRs, CI, and normal merges. No release or production deployment is part of this task.

## State

Owner worktree is db_magic-modernize on modernize/db-magic from fetched origin/master. Original checkout and research note are preserved. Three agents own separate consumer worktrees; root owns the library and publication. db_magic has no configured Actions workflows. Consumer PR CI supplies integrated build coverage; actively authored owner tests can run locally under the existing testing exception.

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

Commit owner API, supply it to consumer agents, publish the library PR and follow available checks. Complete consumer migrations and pins, inspect diffs, review actual published PRs, follow CI and repair failures, then merge normally and clean task worktrees/branches. Record PR numbers and terminal evidence here without commit IDs.
