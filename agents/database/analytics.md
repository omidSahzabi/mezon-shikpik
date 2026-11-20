# V2 analytics contract

Source: view SQL in `backend/schema_v2/migrations/0002_integrity_and_reports.py`; relocated to `analytics` by the organization script. Original-layout views are unqualified; use `analytics.<view>` for the organized layout. These are ordinary views, not persisted summary tables or materialized views.

## Financial definitions

Gross is the sum of list-price item snapshots on paid orders. Sales is gross less snapshotted discounts. Captured includes every succeeded payment attempt, including duplicate charges. Refunded includes completed refunds only. Net sales is sales minus completed refunds; net cash is captures minus completed refunds. Refund requests and failures are not completed cash movements.

Sales dates use order `paid_at` in Asia/Tehran. Refunds in a sales-day row restate that order cohort; the view is not a daily cash-flow ledger. Views preaggregate captures/refunds before joining orders/items to avoid multiplying amounts across independent relationships.

| View | Grain | Output columns and interpretation |
| --- | --- | --- |
| `daily_sales` | Tehran sale date, currency | `sale_date`, `currency`, `order_count`, `gross_amount`, `discount_amount`, `sales_amount`, `captured_amount`, `refunded_amount`, `net_sales_amount`, `net_cash_amount`; paid orders only. |
| `product_sales` | Sold product, currency | `product_id`, `currency`, `units_sold`, `gross_amount`, `discount_amount`, `sales_amount`, `refunded_amount`, `net_sales_amount`; item refund allocations only. `units_sold` counts item rows because V2 has no quantity field. |
| `payment_success_rate` | Provider, Tehran attempt creation date | `provider`, `attempt_date`, `total_attempts`, `successful_attempts`, `terminal_attempts`, `success_rate`, `captured_amount`; succeeded / (succeeded + failed + cancelled), NULL if no terminal attempts. |
| `refund_summary` | Provider, currency, refund status | `provider`, `currency`, `status`, `refund_count`, `requested_amount`, `refunded_amount`; requested_amount is the sum for that status group, not only requested-status records; refunded_amount is nonzero only for completed groups. |
| `course_completion` | Entitled user, course | `user_id`, `course_id`, `access_status`, `total_lessons`, `completed_lessons`, `completion_rate`; published lessons within published chapters, completed_at indicates completion. Includes active and revoked entitlements. Zero lesson denominator yields NULL. |
| `coupon_performance` | Coupon | `coupon_id`, `code`, `paid_orders`, `gross_amount`, `discount_amount`, `sales_amount`, `captured_amount`, `refunded_amount`, `net_sales_amount`; left join retains coupons with zero paid sales. Uses the order's coupon and snapshots, not redemption-row counts. |

Bundle revenue stays on the sold bundle product; no component revenue allocation is invented. Product sales do not attribute extra duplicate captured cash to products. `course_completion` does not require the course product itself to be published; its SQL filters lesson and chapter publication.

For changes, verify double captures, partial/full completed refunds, multiple discounts, empty denominators, zero-sale coupons, bundle sales, and Tehran date boundaries. Add migrations for changed view definitions and preserve consumers' column contracts.
