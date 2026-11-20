# Legacy data dictionary

Source snapshot reviewed 2026-11-19. Declarations below are copied from local model source, without importing Django or accessing a database. They specify ORM types, lengths, nullability, defaults, references, and deletion declarations. `null=True` allows SQL NULL; `blank=True` concerns validation. A Python default is not necessarily a database default. `db_default` is explicit. ForeignKey columns normally append `_id`; `db_column` overrides this. A OneToOneField adds uniqueness. ManyToManyField uses a separate junction table. SlugField/EmailField validator behavior is not a PostgreSQL CHECK.

Read [legacy boundary](legacy.md) for service rules and V2 differences. Table names below are default Django names from app and lowercase model name. This dictionary inventories local domain models, not all installed framework models or a live database.

Unless a primary key is explicitly listed, these app models receive an implicit BigAutoField `id` under the current settings. Auth User also inherits `last_login` (nullable timestamp) and `is_superuser` (boolean). Legacy User inherits `password` and Django group/direct-permission fields; V2 overrides password and junction declarations explicitly. Framework-generated auth junction metadata must be checked against installed Django migrations.


## User: accounts_user

Source: [accounts/models.py](../../backend/accounts/models.py).

| Field | Source declaration |
| --- | --- |
| `phone` | <code>models.CharField( max_length=15, unique=True )</code> |
| `role` | <code>models.CharField( max_length=20, choices=ROLE_CHOICES, default="student" )</code> |
| `is_blocked` | <code>models.BooleanField( default=False )</code> |
| `is_active` | <code>models.BooleanField( default=True )</code> |
| `is_staff` | <code>models.BooleanField( default=False )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |
| `updated_at` | <code>models.DateTimeField( auto_now=True )</code> |

## OTPCode: accounts_otpcode

Source: [accounts/models.py](../../backend/accounts/models.py).

| Field | Source declaration |
| --- | --- |
| `phone` | <code>models.CharField( max_length=15 )</code> |
| `code` | <code>models.CharField( max_length=6 )</code> |
| `is_used` | <code>models.BooleanField( default=False )</code> |
| `expires_at` | <code>models.DateTimeField()</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

## UserSession: accounts_usersession

Source: [accounts/models.py](../../backend/accounts/models.py).

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions" )</code> |
| `session_key` | <code>models.CharField( max_length=255, unique=True )</code> |
| `device_name` | <code>models.CharField( max_length=255, blank=True, null=True )</code> |
| `ip_address` | <code>models.GenericIPAddressField( blank=True, null=True )</code> |
| `user_agent` | <code>models.TextField( blank=True, null=True )</code> |
| `is_active` | <code>models.BooleanField( default=True )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |
| `last_activity` | <code>models.DateTimeField( auto_now=True )</code> |
| `expires_at` | <code>models.DateTimeField()</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
ordering = [
    "-last_activity"
]
```

## Course: courses_course

Source: [courses/models.py](../../backend/courses/models.py).

| Field | Source declaration |
| --- | --- |
| `title` | <code>models.CharField( max_length=255 )</code> |
| `slug` | <code>models.SlugField( unique=True )</code> |
| `description` | <code>models.TextField()</code> |
| `thumbnail` | <code>models.ImageField( upload_to="courses/", null=True, blank=True )</code> |
| `price` | <code>models.PositiveIntegerField()</code> |
| `is_published` | <code>models.BooleanField( default=False )</code> |
| `is_free` | <code>models.BooleanField( default=False )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |
| `updated_at` | <code>models.DateTimeField( auto_now=True )</code> |

## Chapter: courses_chapter

Source: [courses/models.py](../../backend/courses/models.py).

| Field | Source declaration |
| --- | --- |
| `course` | <code>models.ForeignKey( Course, on_delete=models.CASCADE, related_name="chapters" )</code> |
| `title` | <code>models.CharField( max_length=255 )</code> |
| `order` | <code>models.PositiveIntegerField( default=0 )</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
ordering = [
    "order"
]
```

## Lesson: courses_lesson

Source: [courses/models.py](../../backend/courses/models.py).

| Field | Source declaration |
| --- | --- |
| `chapter` | <code>models.ForeignKey( Chapter, on_delete=models.CASCADE, related_name="lessons" )</code> |
| `title` | <code>models.CharField( max_length=255 )</code> |
| `description` | <code>models.TextField( blank=True )</code> |
| `video` | <code>models.FileField( upload_to="videos/" )</code> |
| `duration` | <code>models.PositiveIntegerField( default=0 )</code> |
| `order` | <code>models.PositiveIntegerField( default=0 )</code> |
| `is_free` | <code>models.BooleanField( default=False )</code> |
| `is_published` | <code>models.BooleanField( default=False )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |
| `updated_at` | <code>models.DateTimeField( auto_now=True )</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
ordering = [
    "order"
]
```

## LessonProgress: courses_lessonprogress

Source: [courses/models.py](../../backend/courses/models.py).

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE )</code> |
| `lesson` | <code>models.ForeignKey( Lesson, on_delete=models.CASCADE, related_name="progresses" )</code> |
| `watched_seconds` | <code>models.PositiveIntegerField( default=0 )</code> |
| `completed` | <code>models.BooleanField( default=False )</code> |
| `updated_at` | <code>models.DateTimeField( auto_now=True )</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
unique_together = (
    "user",
    "lesson"
)
```

## Pattern: patterns_pattern

Source: [patterns/models.py](../../backend/patterns/models.py).

| Field | Source declaration |
| --- | --- |
| `title` | <code>models.CharField( max_length=255 )</code> |
| `slug` | <code>models.SlugField( unique=True )</code> |
| `description` | <code>models.TextField( blank=True )</code> |
| `thumbnail` | <code>models.ImageField( upload_to="patterns/", null=True, blank=True )</code> |
| `file` | <code>models.FileField( upload_to="patterns/files/" )</code> |
| `price` | <code>models.PositiveIntegerField()</code> |
| `is_published` | <code>models.BooleanField( default=False )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

## Product: commerce_product

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `title` | <code>models.CharField( max_length=255 )</code> |
| `type` | <code>models.CharField( max_length=20, choices=TYPES )</code> |
| `price` | <code>models.PositiveIntegerField()</code> |
| `course` | <code>models.ForeignKey( Course, null=True, blank=True, on_delete=models.CASCADE )</code> |
| `pattern` | <code>models.ForeignKey( Pattern, null=True, blank=True, on_delete=models.CASCADE )</code> |
| `is_active` | <code>models.BooleanField( default=True )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

## Discount: commerce_discount

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `code` | <code>models.CharField( max_length=50, unique=True )</code> |
| `percent` | <code>models.PositiveIntegerField()</code> |
| `max_usage` | <code>models.PositiveIntegerField( null=True, blank=True )</code> |
| `used_count` | <code>models.PositiveIntegerField( default=0 )</code> |
| `is_active` | <code>models.BooleanField( default=True )</code> |
| `start_date` | <code>models.DateTimeField( null=True, blank=True )</code> |
| `end_date` | <code>models.DateTimeField( null=True, blank=True )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

## Cart: commerce_cart

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.OneToOneField( settings.AUTH_USER_MODEL, on_delete=models.CASCADE )</code> |
| `discount` | <code>models.ForeignKey( Discount, null=True, blank=True, on_delete=models.SET_NULL )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

## CartItem: commerce_cartitem

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `cart` | <code>models.ForeignKey( Cart, related_name="items", on_delete=models.CASCADE )</code> |
| `product` | <code>models.ForeignKey( Product, on_delete=models.CASCADE )</code> |
| `quantity` | <code>models.PositiveIntegerField( default=1 )</code> |

## Order: commerce_order

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE )</code> |
| `status` | <code>models.CharField( max_length=20, choices=STATUS, default="pending" )</code> |
| `total_price` | <code>models.PositiveIntegerField()</code> |
| `discount` | <code>models.ForeignKey( Discount, null=True, blank=True, on_delete=models.SET_NULL )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

## OrderItem: commerce_orderitem

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `order` | <code>models.ForeignKey( Order, related_name="items", on_delete=models.CASCADE )</code> |
| `product` | <code>models.ForeignKey( Product, related_name="order_items", on_delete=models.CASCADE )</code> |
| `quantity` | <code>models.PositiveIntegerField( default=1 )</code> |
| `price` | <code>models.PositiveIntegerField()</code> |

## Purchase: commerce_purchase

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases" )</code> |
| `product` | <code>models.ForeignKey( Product, on_delete=models.CASCADE )</code> |
| `order` | <code>models.ForeignKey( Order, on_delete=models.CASCADE )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
unique_together = (
    "user",
    "product"
)
```

## Payment: commerce_payment

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `order` | <code>models.OneToOneField( Order, on_delete=models.CASCADE, related_name="payment" )</code> |
| `amount` | <code>models.PositiveIntegerField()</code> |
| `authority` | <code>models.CharField( max_length=255, null=True, blank=True )</code> |
| `ref_id` | <code>models.CharField( max_length=255, null=True, blank=True )</code> |
| `status` | <code>models.CharField( max_length=20, choices=STATUS, default="pending" )</code> |
| `gateway_response` | <code>models.JSONField( null=True, blank=True )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

## Wishlist: commerce_wishlist

Source: [commerce/models.py](../../backend/commerce/models.py).

| Field | Source declaration |
| --- | --- |
| `user` | <code>models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist" )</code> |
| `product` | <code>models.ForeignKey( Product, on_delete=models.CASCADE, related_name="wishlists" )</code> |
| `created_at` | <code>models.DateTimeField( auto_now_add=True )</code> |

Model metadata (ORM declarations; SQL migrations add further rules):

```python
unique_together = (
    "user",
    "product"
)
```

Inventory: 17 local concrete models; 100 explicitly declared field entries (including composite primary-key declarations and many-to-many declarations). Inherited and implicit fields are described above and are not included in that entry count.
