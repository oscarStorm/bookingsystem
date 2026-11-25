# Single-restaurant MVP on a multi-restaurant-ready schema

Status: accepted

`restaurant_id` is kept on every restaurant-scoped table and all queries filter by it, and staff
belong to a restaurant — but the MVP seeds exactly one restaurant and there is no restaurant
selection or tenant-management UI. This keeps the schema ready for multiple restaurants without
redesign later, at the cost of a foreign key on every query now. The original PRD scoped
multi-restaurant SaaS out; this ADR records that the schema deliberately does NOT follow that
scoping.
