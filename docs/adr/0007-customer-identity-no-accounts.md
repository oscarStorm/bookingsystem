# Customer identity: no accounts, email is not an identity

Status: accepted

Customers have no accounts. `email` on the customer record is contact information and is NOT
unique — multiple reservations may share an email. Each reservation gets its own dedicated customer
row (deleted during anonymization). Online reservations always have a customer and a manage
token; staff-created phone/walk-in reservations record the creating staff member, and anonymous
walk-ins may have neither customer nor token. `source` records how the reservation was created
(`online`, `phone`, `walk_in`).
