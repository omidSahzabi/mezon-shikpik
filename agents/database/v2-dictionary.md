# V2 data dictionary

Source snapshot reviewed 2026-11-19. Declarations below are copied from local model source, without importing Django or accessing a database. They specify ORM types, lengths, nullability, defaults, references, and deletion declarations. `null=True` allows SQL NULL; `blank=True` concerns validation. A Python default is not necessarily a database default. `db_default` is explicit. ForeignKey columns normally append `_id`; `db_column` overrides this. A OneToOneField adds uniqueness. ManyToManyField uses a separate junction table. SlugField/EmailField validator behavior is not a PostgreSQL CHECK.

Read [architecture](architecture.md) for physical schemas and framework tables, [rules](rules.md) for SQL-only constraints/triggers, and [security](security.md) for permissions. Current models still use unqualified table names. `text(n)` means CharField(max_length=n); `money()` means DecimalField(max_digits=14, decimal_places=0); `fk()` means ForeignKey with PROTECT. `uq` constructs a UniqueConstraint; `ck` constructs a CheckConstraint; `enum` constructs allowed-value CHECKs. `Operational` contributes `created_at = DateTimeField(db_default=Now())` and `updated_at = DateTimeField(db_default=Now(), auto_now=True)`.

Unless a primary key is explicitly listed, these app models receive an implicit BigAutoField `id` under the current settings. Auth User also inherits `last_login` (nullable timestamp) and `is_superuser` (boolean). Legacy User inherits `password` and Django group/direct-permission fields; V2 overrides password and junction declarations explicitly. Framework-generated auth junction metadata must be checked against installed Django migrations.


## User: entity.users

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `public_id` | <code>models.UUIDField(default=uuid.uuid4, unique=True)</code> |
| `phone` | <code>text(16, unique=True)</code> |
| `email` | <code>models.EmailField(null=True)</code> |
| `password` | <code>text(128, default='', db_default='')</code> |
| `is_active` | <code>models.BooleanField(default=True, db_default=True)</code> |
| `is_staff` | <code>models.BooleanField(default=False, db_default=False)</code> |
| `groups` | <code>models.ManyToManyField('auth.Group', db_table='users_groups', blank=True)</code> |
| `user_permissions` | <code>models.ManyToManyField('auth.Permission', db_table='users_user_permissions', blank=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'users'
constraints = [models.UniqueConstraint(Lower('email'), condition=Q(email__isnull=False), name='users_email_ci_uq'), ck('phone_e164', Q(phone__regex=r'^\+[1-9][0-9]{7,14}$'))]
```

## UserProfile: profiles.user_profiles

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)</code> |
| `first_name` | <code>text(100, default='', db_default='')</code> |
| `last_name` | <code>text(100, default='', db_default='')</code> |
| `avatar_key` | <code>text(512, null=True)</code> |
| `birth_date` | <code>models.DateField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'user_profiles'
```

## StaffProfile: profiles.staff_profiles

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)</code> |
| `display_name` | <code>text(150)</code> |
| `is_enabled` | <code>models.BooleanField(default=True, db_default=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'staff_profiles'
```

## InstructorProfile: profiles.instructor_profiles

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)</code> |
| `display_name` | <code>text(150)</code> |
| `bio` | <code>models.TextField(default='', db_default='')</code> |
| `is_public` | <code>models.BooleanField(default=False, db_default=False)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'instructor_profiles'
```

## OTPChallenge: security.otp_challenges

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.ForeignKey(User, null=True, on_delete=models.SET_NULL)</code> |
| `phone` | <code>text(16)</code> |
| `purpose` | <code>text(24)</code> |
| `code_hash` | <code>text(255)</code> |
| `attempts` | <code>models.SmallIntegerField(default=0, db_default=0)</code> |
| `expires_at` | <code>models.DateTimeField()</code> |
| `consumed_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'otp_challenges'
constraints = [ck('attempts_range', Q(attempts__gte=0, attempts__lte=10))]
indexes = [models.Index(fields=['phone', 'purpose', 'expires_at'])]
```

## AuthSession: security.auth_sessions

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>fk(User)</code> |
| `token_hash` | <code>text(64, unique=True)</code> |
| `expires_at` | <code>models.DateTimeField()</code> |
| `revoked_at` | <code>models.DateTimeField(null=True)</code> |
| `last_seen_at` | <code>models.DateTimeField(null=True)</code> |
| `device_info` | <code>models.JSONField(default=dict, db_default={})</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'auth_sessions'
indexes = [models.Index(fields=['user', 'expires_at'])]
```

## Product: entity.products

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `slug` | <code>models.SlugField(max_length=180, unique=True)</code> |
| `title` | <code>text(255)</code> |
| `kind` | <code>text(16)</code> |
| `status` | <code>text(16, default='draft', db_default='draft')</code> |
| `description` | <code>models.TextField(default='', db_default='')</code> |
| `thumbnail_key` | <code>text(512, null=True)</code> |
| `published_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'products'
constraints = [enum('kind', 'course pattern bundle'), enum('status', 'draft published archived')]
```

## Category: entity.categories

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `parent` | <code>fk('self', null=True)</code> |
| `slug` | <code>models.SlugField(max_length=150, unique=True)</code> |
| `name` | <code>text(150)</code> |
| `sort_order` | <code>models.IntegerField(default=0, db_default=0)</code> |
| `is_active` | <code>models.BooleanField(default=True, db_default=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'categories'
constraints = [ck('not_self', ~Q(parent=F('id')))]
```

## ProductCategory: profiles.product_categories

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `pk` | <code>models.CompositePrimaryKey('product_id', 'category_id')</code> |
| `product` | <code>models.ForeignKey(Product, on_delete=models.CASCADE)</code> |
| `category` | <code>models.ForeignKey(Category, on_delete=models.CASCADE)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'product_categories'
```

## Course: entity.courses

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `product` | <code>models.OneToOneField(Product, on_delete=models.PROTECT)</code> |
| `instructor` | <code>fk(InstructorProfile, null=True)</code> |
| `level` | <code>text(20, default='beginner', db_default='beginner')</code> |
| `summary` | <code>models.TextField(default='', db_default='')</code> |
| `estimated_minutes` | <code>models.IntegerField(default=0, db_default=0)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'courses'
constraints = [ck('minutes_positive', Q(estimated_minutes__gte=0)), enum('level', 'beginner intermediate advanced')]
```

## Chapter: profiles.chapters

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `course` | <code>fk(Course)</code> |
| `title` | <code>text(255)</code> |
| `position` | <code>models.IntegerField()</code> |
| `is_published` | <code>models.BooleanField(default=False, db_default=False)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'chapters'
constraints = [uq('course', 'position'), ck('position_positive', Q(position__gte=0))]
```

## Lesson: entity.lessons

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `chapter` | <code>fk(Chapter)</code> |
| `title` | <code>text(255)</code> |
| `position` | <code>models.IntegerField()</code> |
| `duration_seconds` | <code>models.IntegerField(default=0, db_default=0)</code> |
| `is_preview` | <code>models.BooleanField(default=False, db_default=False)</code> |
| `is_published` | <code>models.BooleanField(default=False, db_default=False)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'lessons'
constraints = [uq('chapter', 'position'), ck('positive', Q(position__gte=0, duration_seconds__gte=0))]
```

## LessonAsset: profiles.lesson_assets

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `lesson` | <code>fk(Lesson)</code> |
| `kind` | <code>text(20)</code> |
| `storage_key` | <code>text(512)</code> |
| `mime_type` | <code>text(120)</code> |
| `size_bytes` | <code>models.BigIntegerField()</code> |
| `position` | <code>models.IntegerField(default=0, db_default=0)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'lesson_assets'
constraints = [uq('lesson', 'position'), ck('size_positive', Q(size_bytes__gte=0))]
```

## Pattern: entity.patterns

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `product` | <code>models.OneToOneField(Product, on_delete=models.PROTECT)</code> |
| `description` | <code>models.TextField(default='', db_default='')</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'patterns'
```

## PatternVariant: profiles.pattern_variants

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `pattern` | <code>fk(Pattern)</code> |
| `size_label` | <code>text(40)</code> |
| `sort_order` | <code>models.IntegerField(default=0, db_default=0)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'pattern_variants'
constraints = [uq('pattern', 'size_label'), uq('id', 'pattern')]
```

## PatternRelease: profiles.pattern_releases

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `pattern` | <code>fk(Pattern)</code> |
| `version` | <code>text(32)</code> |
| `status` | <code>text(16, default='draft', db_default='draft')</code> |
| `released_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'pattern_releases'
constraints = [uq('pattern', 'version'), uq('id', 'pattern'), enum('status', 'draft published archived')]
```

## PatternFile: profiles.pattern_files

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `release` | <code>fk(PatternRelease)</code> |
| `variant` | <code>fk(PatternVariant, null=True)</code> |
| `pattern` | <code>fk(Pattern)</code> |
| `file_kind` | <code>text(30)</code> |
| `storage_key` | <code>text(512)</code> |
| `checksum_sha256` | <code>text(64)</code> |
| `size_bytes` | <code>models.BigIntegerField()</code> |
| `display_name` | <code>text(255)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'pattern_files'
constraints = [models.UniqueConstraint(fields=['release', 'variant', 'file_kind'], nulls_distinct=False, name='pattern_files_release_variant_kind_uq'), ck('size_positive', Q(size_bytes__gt=0))]
```

## Bundle: entity.bundles

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `product` | <code>models.OneToOneField(Product, on_delete=models.PROTECT)</code> |
| `description` | <code>models.TextField(default='', db_default='')</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'bundles'
```

## BundleItem: profiles.bundle_items

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `pk` | <code>models.CompositePrimaryKey('bundle_id', 'product_id')</code> |
| `bundle` | <code>fk(Bundle)</code> |
| `product` | <code>fk(Product)</code> |
| `position` | <code>models.IntegerField()</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'bundle_items'
constraints = [uq('bundle', 'position'), ck('position_positive', Q(position__gte=0))]
```

## ProductPrice: transactions.product_prices

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `product` | <code>fk(Product)</code> |
| `amount` | <code>money()</code> |
| `valid_from` | <code>models.DateTimeField()</code> |
| `valid_until` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'product_prices'
constraints = [ck('amount_positive', Q(amount__gte=0)), ck('valid_interval', Q(valid_until__isnull=True) | Q(valid_until__gt=F('valid_from'))), ExclusionConstraint(name='product_prices_no_overlap', expressions=[('product', RangeOperators.EQUAL), (models.Func('valid_from', 'valid_until', Value('[)'), function='TSTZRANGE', output_field=DateTimeRangeField()), RangeOperators.OVERLAPS)])]
```

## Promotion: entity.promotions

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `name` | <code>text(150)</code> |
| `discount_type` | <code>text(12)</code> |
| `value` | <code>models.DecimalField(max_digits=14, decimal_places=2)</code> |
| `starts_at` | <code>models.DateTimeField()</code> |
| `ends_at` | <code>models.DateTimeField()</code> |
| `is_active` | <code>models.BooleanField(default=False, db_default=False)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'promotions'
constraints = [enum('discount_type', 'percent fixed'), ck('valid', Q(value__gt=0, ends_at__gt=F('starts_at')) & (~Q(discount_type='percent') | Q(value__lte=100)))]
```

## PromotionProduct: profiles.promotion_products

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `pk` | <code>models.CompositePrimaryKey('promotion_id', 'product_id')</code> |
| `promotion` | <code>fk(Promotion)</code> |
| `product` | <code>fk(Product)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'promotion_products'
```

## Coupon: entity.coupons

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `promotion` | <code>fk(Promotion)</code> |
| `code` | <code>text(80)</code> |
| `usage_limit` | <code>models.IntegerField(null=True)</code> |
| `per_user_limit` | <code>models.IntegerField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'coupons'
constraints = [models.UniqueConstraint(Upper('code'), name='coupon_code_ci_uq'), ck('limits', (Q(usage_limit__isnull=True) | Q(usage_limit__gt=0)) & (Q(per_user_limit__isnull=True) | Q(per_user_limit__gt=0)))]
```

## Cart: transactions.carts

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>fk(User)</code> |
| `status` | <code>text(16, default='active', db_default='active')</code> |
| `expires_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'carts'
constraints = [models.UniqueConstraint(fields=['user'], condition=Q(status='active'), name='cart_active_user_uq'), enum('status', 'active converted expired abandoned')]
```

## CartItem: transactions.cart_items

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `cart` | <code>models.ForeignKey(Cart, on_delete=models.CASCADE)</code> |
| `product` | <code>fk(Product)</code> |
| `added_at` | <code>models.DateTimeField(db_default=Now())</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'cart_items'
constraints = [uq('cart', 'product')]
```

## Order: transactions.orders

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `public_id` | <code>models.UUIDField(default=uuid.uuid4, unique=True)</code> |
| `order_number` | <code>text(32, unique=True)</code> |
| `user` | <code>fk(User)</code> |
| `status` | <code>text(24, default='pending', db_default='pending')</code> |
| `subtotal` | <code>money()</code> |
| `discount_total` | <code>money(default=0, db_default=0)</code> |
| `payable_total` | <code>money()</code> |
| `currency` | <code>text(3, default='IRR', db_default='IRR')</code> |
| `coupon` | <code>fk(Coupon, null=True)</code> |
| `paid_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'orders'
constraints = [enum('status', 'pending paid cancelled expired'), ck('amounts', Q(subtotal__gte=0, discount_total__gte=0, payable_total__gte=0, payable_total=F('subtotal')-F('discount_total'))), ck('currency', Q(currency='IRR')), ck('paid_time', ~Q(status='paid') | Q(paid_at__isnull=False))]
indexes = [models.Index(fields=['user', '-created_at']), models.Index(fields=['status', 'created_at'])]
```

## OrderItem: transactions.order_items

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `order` | <code>fk(Order)</code> |
| `product` | <code>fk(Product)</code> |
| `product_title` | <code>text(255)</code> |
| `product_kind` | <code>text(16)</code> |
| `unit_price` | <code>money()</code> |
| `discount_amount` | <code>money(default=0, db_default=0)</code> |
| `final_amount` | <code>money()</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'order_items'
constraints = [uq('order', 'product'), uq('id', 'order'), enum('product_kind', 'course pattern bundle'), ck('amounts', Q(unit_price__gte=0, discount_amount__gte=0, final_amount__gte=0, final_amount=F('unit_price')-F('discount_amount')))]
```

## BundlePurchaseSnapshot: events.bundle_purchase_snapshots

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `id` | <code>models.BigAutoField(primary_key=True)</code> |
| `order_item` | <code>fk(OrderItem)</code> |
| `product` | <code>fk(Product)</code> |
| `product_title` | <code>text(255)</code> |
| `product_kind` | <code>text(16)</code> |
| `position` | <code>models.IntegerField()</code> |
| `created_at` | <code>models.DateTimeField(db_default=Now())</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'bundle_purchase_snapshots'
constraints = [uq('order_item', 'product'), uq('order_item', 'position'), enum('product_kind', 'course pattern'), ck('position_positive', Q(position__gte=0))]
```

## OrderDiscount: transactions.order_discounts

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `order` | <code>fk(Order)</code> |
| `order_item` | <code>fk(OrderItem, null=True)</code> |
| `promotion` | <code>fk(Promotion, null=True)</code> |
| `code_snapshot` | <code>text(80, null=True)</code> |
| `description` | <code>text(255)</code> |
| `amount` | <code>money()</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'order_discounts'
constraints = [ck('positive', Q(amount__gt=0))]
```

## CouponRedemption: transactions.coupon_redemptions

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `coupon` | <code>fk(Coupon)</code> |
| `user` | <code>fk(User)</code> |
| `order` | <code>models.OneToOneField(Order, on_delete=models.PROTECT)</code> |
| `redeemed_at` | <code>models.DateTimeField(db_default=Now())</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'coupon_redemptions'
constraints = [uq('coupon', 'order')]
```

## PaymentAttempt: transactions.payment_attempts

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `public_id` | <code>models.UUIDField(default=uuid.uuid4, unique=True)</code> |
| `order` | <code>fk(Order)</code> |
| `provider` | <code>text(32)</code> |
| `authority` | <code>text(255, null=True)</code> |
| `reference` | <code>text(255, null=True)</code> |
| `amount` | <code>money()</code> |
| `status` | <code>text(24, default='initiated', db_default='initiated')</code> |
| `idempotency_key` | <code>text(128, unique=True)</code> |
| `verified_at` | <code>models.DateTimeField(null=True)</code> |
| `failure_code` | <code>text(80, null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'payment_attempts'
constraints = [enum('status', 'initiated pending succeeded failed cancelled'), ck('positive', Q(amount__gte=0)), ck('verified', ~Q(status='succeeded') | Q(verified_at__isnull=False)), models.UniqueConstraint(fields=['provider', 'authority'], condition=Q(authority__isnull=False), name='payment_provider_authority_uq'), models.UniqueConstraint(fields=['provider', 'reference'], condition=Q(reference__isnull=False), name='payment_provider_reference_uq')]
indexes = [models.Index(fields=['order', '-created_at'])]
```

## PaymentEvent: events.payment_events

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `payment` | <code>fk(PaymentAttempt)</code> |
| `event_key` | <code>text(255)</code> |
| `event_type` | <code>text(40)</code> |
| `payload` | <code>models.JSONField(default=dict, db_default={})</code> |
| `received_at` | <code>models.DateTimeField(db_default=Now())</code> |
| `processed_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'payment_events'
constraints = [uq('payment', 'event_key')]
```

## Refund: transactions.refunds

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `payment` | <code>fk(PaymentAttempt)</code> |
| `amount` | <code>money()</code> |
| `status` | <code>text(20, default='requested', db_default='requested')</code> |
| `provider_ref` | <code>text(255, null=True)</code> |
| `reason` | <code>models.TextField(default='', db_default='')</code> |
| `requested_by` | <code>fk(User, null=True, related_name='+', db_column='requested_by')</code> |
| `approved_by` | <code>fk(User, null=True, related_name='+', db_column='approved_by')</code> |
| `completed_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'refunds'
constraints = [enum('status', 'requested approved processing completed failed rejected'), ck('positive', Q(amount__gt=0)), ck('completed_time', ~Q(status='completed') | Q(completed_at__isnull=False)), models.UniqueConstraint(fields=['provider_ref'], condition=Q(provider_ref__isnull=False), name='refund_provider_ref_uq')]
```

## RefundItem: transactions.refund_items

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `refund` | <code>fk(Refund)</code> |
| `order_item` | <code>fk(OrderItem)</code> |
| `amount` | <code>money()</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'refund_items'
constraints = [uq('refund', 'order_item'), ck('positive', Q(amount__gt=0))]
```

## IdempotencyKey: security.idempotency_keys

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `scope` | <code>text(60)</code> |
| `key` | <code>text(128)</code> |
| `request_hash` | <code>text(64)</code> |
| `resource_type` | <code>text(40, null=True)</code> |
| `resource_id` | <code>models.BigIntegerField(null=True)</code> |
| `expires_at` | <code>models.DateTimeField(db_index=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'idempotency_keys'
constraints = [uq('scope', 'key')]
```

## Entitlement: profiles.entitlements

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>fk(User)</code> |
| `product` | <code>fk(Product)</code> |
| `status` | <code>text(16, default='active', db_default='active')</code> |
| `granted_at` | <code>models.DateTimeField(db_default=Now())</code> |
| `revoked_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'entitlements'
constraints = [uq('user', 'product'), enum('status', 'active revoked')]
indexes = [models.Index(fields=['user', 'status'])]
```

## EntitlementGrant: profiles.entitlement_grants

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `entitlement` | <code>fk(Entitlement)</code> |
| `order_item` | <code>fk(OrderItem, null=True)</code> |
| `grant_type` | <code>text(20)</code> |
| `granted_by` | <code>fk(User, null=True, db_column='granted_by')</code> |
| `status` | <code>text(16, default='active', db_default='active')</code> |
| `created_at` | <code>models.DateTimeField(db_default=Now())</code> |
| `revoked_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'entitlement_grants'
constraints = [enum('grant_type', 'purchase manual'), enum('status', 'active revoked'), models.UniqueConstraint(fields=['entitlement', 'order_item'], condition=Q(order_item__isnull=False), name='entitlement_grant_purchase_uq'), ck('source', Q(grant_type='purchase', order_item__isnull=False) | Q(grant_type='manual', order_item__isnull=True, granted_by__isnull=False))]
permissions = [('grant_manual_access', 'Grant audited manual access')]
```

## EntitlementEvent: events.entitlement_events

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `entitlement` | <code>fk(Entitlement)</code> |
| `grant` | <code>fk(EntitlementGrant, null=True)</code> |
| `actor` | <code>models.ForeignKey(User, null=True, on_delete=models.SET_NULL)</code> |
| `action` | <code>text(24)</code> |
| `reason` | <code>models.TextField(default='', db_default='')</code> |
| `created_at` | <code>models.DateTimeField(db_default=Now())</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'entitlement_events'
```

## DownloadGrant: security.download_grants

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `entitlement` | <code>fk(Entitlement)</code> |
| `pattern_file` | <code>fk(PatternFile)</code> |
| `token_hash` | <code>text(64, unique=True)</code> |
| `expires_at` | <code>models.DateTimeField()</code> |
| `used_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'download_grants'
constraints = [ck('expiry', Q(expires_at__gt=F('created_at')))]
```

## LessonProgress: profiles.lesson_progress

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>fk(User)</code> |
| `lesson` | <code>fk(Lesson)</code> |
| `last_position_seconds` | <code>models.IntegerField(default=0, db_default=0)</code> |
| `completed_at` | <code>models.DateTimeField(null=True)</code> |
| `last_watched_at` | <code>models.DateTimeField(db_default=Now())</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'lesson_progress'
constraints = [uq('user', 'lesson'), ck('position_positive', Q(last_position_seconds__gte=0))]
```

## Review: profiles.reviews

Source: [schema_v2/models.py](../../backend/schema_v2/models.py). Includes both Operational timestamps.

| Field | Source declaration |
| --- | --- |
| `user` | <code>fk(User)</code> |
| `product` | <code>fk(Product)</code> |
| `rating` | <code>models.SmallIntegerField()</code> |
| `title` | <code>text(200, null=True)</code> |
| `body` | <code>models.TextField(default='', db_default='')</code> |
| `status` | <code>text(20, default='pending', db_default='pending')</code> |
| `moderated_by` | <code>fk(User, null=True, related_name='+', db_column='moderated_by')</code> |
| `moderated_at` | <code>models.DateTimeField(null=True)</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'reviews'
constraints = [uq('user', 'product'), ck('rating_range', Q(rating__gte=1, rating__lte=5)), enum('status', 'pending approved rejected')]
indexes = [models.Index(fields=['product', 'status', '-created_at'])]
```

## ReviewModeration: events.review_moderations

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `review` | <code>fk(Review)</code> |
| `moderator` | <code>fk(User)</code> |
| `action` | <code>text(20)</code> |
| `reason` | <code>models.TextField(default='', db_default='')</code> |
| `created_at` | <code>models.DateTimeField(db_default=Now())</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'review_moderations'
```

## AuditLog: events.audit_logs

Source: [schema_v2/models.py](../../backend/schema_v2/models.py).

| Field | Source declaration |
| --- | --- |
| `actor` | <code>models.ForeignKey(User, null=True, on_delete=models.SET_NULL)</code> |
| `action` | <code>text(100)</code> |
| `entity_type` | <code>text(80)</code> |
| `entity_id` | <code>text(80)</code> |
| `before_data` | <code>models.JSONField(null=True)</code> |
| `after_data` | <code>models.JSONField(null=True)</code> |
| `request_id` | <code>models.UUIDField(null=True)</code> |
| `ip_address` | <code>models.GenericIPAddressField(null=True)</code> |
| `created_at` | <code>models.DateTimeField(db_default=Now())</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
db_table = 'audit_logs'
indexes = [models.Index(fields=['entity_type', 'entity_id', '-created_at']), models.Index(fields=['actor', '-created_at'])]
```

Inventory: 43 local concrete models; 232 explicitly declared field entries (including composite primary-key declarations and many-to-many declarations). Inherited and implicit fields are described above and are not included in that entry count.
