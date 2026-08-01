# The Tips data boundaries

- Golf O'Clock is the source for reservation timing, bay use, reservation status, customer identity attached to a booking, and Golf O'Clock membership or package fields.
- Golf O'Clock membership fields are supporting context, not confirmed billing truth. Use completed positive-price Square membership orders, founding-member records, and explicitly confirmed overrides for billing-active membership decisions.
- Golf O'Clock payment arrays and credit usages describe booking-system records. Do not present them as full realized venue revenue without reconciliation to Square.
- Use raw reservation JSON when nested duration, room, payment, or credit details matter. A flattened CSV can discard structure.
- Customer names, emails, phone numbers, reservation histories, and balances are confidential. Minimize collection, do not commit them, and do not place them in broadly shared documents.
- A live API response reflects the query time only. Include the exact date range and retrieval time when the result will drive an operational decision.
