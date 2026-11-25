# Seating model: fixed first window, derived second window, max two seatings

Status: accepted

Online reservations start on a 15-minute grid within the first seating window
[17:30, 18:15]. The second seating window is not stored separately; it is derived as
[first_start + duration + buffer, first_last_start + duration + buffer] = [19:45, 20:30].
A table may have at most two active reservations per local evening (all sources count; staff may
override). When both windows are used on one table, the second start must be at least
first start + duration + buffer (135 min) — this falls out of the protected intervals, so it
holds regardless of which seating was booked first (order independence).

Considered options: a fully dynamic second window that shifts with the first booking (rejected:
harder to display and to reason about; the fixed-plus-derived model with the pair rule gives the
same order independence with simpler configuration in `booking_rules`).
