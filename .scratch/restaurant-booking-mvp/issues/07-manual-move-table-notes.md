# 07: Manual table move and table notes

**What to build:** The staff move endpoint: `POST …/move {table_ids}` performs an atomic in-place allocation change for unlocked, unstarted reservations only, preserving reservation id, times, customer, and manage_token (ADR-0006) — old and new allocation rows change in one transaction. Plus staff-only table notes CRUD: content with optional expiry, visible to staff only, never blocking capacity.

**Blocked by:** 06.

**Status:** ready-for-agent

- [ ] Move preserves reservation id/times/customer/token and changes only allocations, atomically
- [ ] Move is rejected for locked or already-started reservations
- [ ] Table notes can be created, listed, and deleted with optional expiry; notes never affect availability or capacity
