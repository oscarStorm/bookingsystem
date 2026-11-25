# Opening hours: three times per weekday and a kitchen cutoff

Status: accepted

Each weekday's opening hours record has `open_time`, `kitchen_close_time`, and `close_time`.
A reservation must start at or after `open_time` and strictly before `kitchen_close_time`, and its
occupied time must end by `close_time`. The kitchen cutoff applies to ALL reservations, including
staff phone/walk-in bookings. The buffer never extends a guest's stay past closing. If
`close_time` ≤ `open_time`, closing is on the following calendar day (00:00 = next midnight).
A weekday without a record is closed. Seed: Monday closed; Tue–Sun 17:30 / 21:00 / 00:00.

Considered options: a two-time model (open/close) with close_time ≥ 22:30 (rejected: the kitchen
cutoff is the real operational constraint — guests may be seated until 20:30 but must arrive
before 21:00, and the kitchen closes before the restaurant).
