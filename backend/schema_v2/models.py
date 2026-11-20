import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.db import models
from django.db.models import F, Q, Value
from django.db.models.functions import Lower, Now, Upper


def text(n, **kw):
    return models.CharField(max_length=n, **kw)


def money(**kw):
    return models.DecimalField(max_digits=14, decimal_places=0, **kw)


def fk(to, **kw):
    return models.ForeignKey(to, on_delete=models.PROTECT, **kw)


def uq(*fields):
    return models.UniqueConstraint(fields=fields, name='%(class)s_' + '_'.join(fields) + '_uq')


def ck(name, condition):
    return models.CheckConstraint(condition=condition, name='%(class)s_' + name)


def enum(field, values):
    return ck(field + '_enum', Q(**{field + '__in': values.split()}))


class Operational(models.Model):
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now(), auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **kwargs):
        user = self.model(phone=phone, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **kwargs):
        kwargs.update(is_staff=True, is_superuser=True)
        return self.create_user(phone, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin, Operational):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True)
    phone = text(16, unique=True)
    email = models.EmailField(null=True)
    password = text(128, default='', db_default='')
    is_active = models.BooleanField(default=True, db_default=True)
    is_staff = models.BooleanField(default=False, db_default=False)
    groups = models.ManyToManyField('auth.Group', db_table='users_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', db_table='users_user_permissions', blank=True)
    USERNAME_FIELD = 'phone'
    objects = UserManager()

    class Meta:
        db_table = 'users'
        constraints = [models.UniqueConstraint(Lower('email'), condition=Q(email__isnull=False), name='users_email_ci_uq'), ck('phone_e164', Q(phone__regex=r'^\+[1-9][0-9]{7,14}$'))]


class UserProfile(Operational):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)
    first_name = text(100, default='', db_default='')
    last_name = text(100, default='', db_default='')
    avatar_key = text(512, null=True)
    birth_date = models.DateField(null=True)

    class Meta:
        db_table = 'user_profiles'


class StaffProfile(Operational):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)
    display_name = text(150)
    is_enabled = models.BooleanField(default=True, db_default=True)

    class Meta:
        db_table = 'staff_profiles'


class InstructorProfile(Operational):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)
    display_name = text(150)
    bio = models.TextField(default='', db_default='')
    is_public = models.BooleanField(default=False, db_default=False)

    class Meta:
        db_table = 'instructor_profiles'


class OTPChallenge(Operational):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    phone = text(16)
    purpose = text(24)
    code_hash = text(255)
    attempts = models.SmallIntegerField(default=0, db_default=0)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'otp_challenges'
        constraints = [ck('attempts_range', Q(attempts__gte=0, attempts__lte=10))]
        indexes = [models.Index(fields=['phone', 'purpose', 'expires_at'])]


class AuthSession(Operational):
    user = fk(User)
    token_hash = text(64, unique=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)
    last_seen_at = models.DateTimeField(null=True)
    device_info = models.JSONField(default=dict, db_default={})

    class Meta:
        db_table = 'auth_sessions'
        indexes = [models.Index(fields=['user', 'expires_at'])]


class Product(Operational):
    slug = models.SlugField(max_length=180, unique=True)
    title = text(255)
    kind = text(16)
    status = text(16, default='draft', db_default='draft')
    description = models.TextField(default='', db_default='')
    thumbnail_key = text(512, null=True)
    published_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'products'
        constraints = [enum('kind', 'course pattern bundle'), enum('status', 'draft published archived')]


class Category(Operational):
    parent = fk('self', null=True)
    slug = models.SlugField(max_length=150, unique=True)
    name = text(150)
    sort_order = models.IntegerField(default=0, db_default=0)
    is_active = models.BooleanField(default=True, db_default=True)

    class Meta:
        db_table = 'categories'
        constraints = [ck('not_self', ~Q(parent=F('id')))]


class ProductCategory(models.Model):
    pk = models.CompositePrimaryKey('product_id', 'category_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_categories'


class Course(Operational):
    product = models.OneToOneField(Product, on_delete=models.PROTECT)
    instructor = fk(InstructorProfile, null=True)
    level = text(20, default='beginner', db_default='beginner')
    summary = models.TextField(default='', db_default='')
    estimated_minutes = models.IntegerField(default=0, db_default=0)

    class Meta:
        db_table = 'courses'
        constraints = [ck('minutes_positive', Q(estimated_minutes__gte=0)), enum('level', 'beginner intermediate advanced')]


class Chapter(Operational):
    course = fk(Course)
    title = text(255)
    position = models.IntegerField()
    is_published = models.BooleanField(default=False, db_default=False)

    class Meta:
        db_table = 'chapters'
        constraints = [uq('course', 'position'), ck('position_positive', Q(position__gte=0))]


class Lesson(Operational):
    chapter = fk(Chapter)
    title = text(255)
    position = models.IntegerField()
    duration_seconds = models.IntegerField(default=0, db_default=0)
    is_preview = models.BooleanField(default=False, db_default=False)
    is_published = models.BooleanField(default=False, db_default=False)

    class Meta:
        db_table = 'lessons'
        constraints = [uq('chapter', 'position'), ck('positive', Q(position__gte=0, duration_seconds__gte=0))]


class LessonAsset(Operational):
    lesson = fk(Lesson)
    kind = text(20)
    storage_key = text(512)
    mime_type = text(120)
    size_bytes = models.BigIntegerField()
    position = models.IntegerField(default=0, db_default=0)

    class Meta:
        db_table = 'lesson_assets'
        constraints = [uq('lesson', 'position'), ck('size_positive', Q(size_bytes__gte=0))]


class Pattern(Operational):
    product = models.OneToOneField(Product, on_delete=models.PROTECT)
    description = models.TextField(default='', db_default='')

    class Meta:
        db_table = 'patterns'


class PatternVariant(Operational):
    pattern = fk(Pattern)
    size_label = text(40)
    sort_order = models.IntegerField(default=0, db_default=0)

    class Meta:
        db_table = 'pattern_variants'
        constraints = [uq('pattern', 'size_label'), uq('id', 'pattern')]


class PatternRelease(Operational):
    pattern = fk(Pattern)
    version = text(32)
    status = text(16, default='draft', db_default='draft')
    released_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'pattern_releases'
        constraints = [uq('pattern', 'version'), uq('id', 'pattern'), enum('status', 'draft published archived')]


class PatternFile(Operational):
    release = fk(PatternRelease)
    variant = fk(PatternVariant, null=True)
    pattern = fk(Pattern)
    file_kind = text(30)
    storage_key = text(512)
    checksum_sha256 = text(64)
    size_bytes = models.BigIntegerField()
    display_name = text(255)

    class Meta:
        db_table = 'pattern_files'
        constraints = [models.UniqueConstraint(fields=['release', 'variant', 'file_kind'], nulls_distinct=False, name='pattern_files_release_variant_kind_uq'), ck('size_positive', Q(size_bytes__gt=0))]


class Bundle(Operational):
    product = models.OneToOneField(Product, on_delete=models.PROTECT)
    description = models.TextField(default='', db_default='')

    class Meta:
        db_table = 'bundles'


class BundleItem(models.Model):
    pk = models.CompositePrimaryKey('bundle_id', 'product_id')
    bundle = fk(Bundle)
    product = fk(Product)
    position = models.IntegerField()

    class Meta:
        db_table = 'bundle_items'
        constraints = [uq('bundle', 'position'), ck('position_positive', Q(position__gte=0))]


class ProductPrice(Operational):
    product = fk(Product)
    amount = money()
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True)

    class Meta:
        db_table = 'product_prices'
        constraints = [ck('amount_positive', Q(amount__gte=0)), ck('valid_interval', Q(valid_until__isnull=True) | Q(valid_until__gt=F('valid_from'))), ExclusionConstraint(name='product_prices_no_overlap', expressions=[('product', RangeOperators.EQUAL), (models.Func('valid_from', 'valid_until', Value('[)'), function='TSTZRANGE', output_field=DateTimeRangeField()), RangeOperators.OVERLAPS)])]


class Promotion(Operational):
    name = text(150)
    discount_type = text(12)
    value = models.DecimalField(max_digits=14, decimal_places=2)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=False, db_default=False)

    class Meta:
        db_table = 'promotions'
        constraints = [enum('discount_type', 'percent fixed'), ck('valid', Q(value__gt=0, ends_at__gt=F('starts_at')) & (~Q(discount_type='percent') | Q(value__lte=100)))]


class PromotionProduct(models.Model):
    pk = models.CompositePrimaryKey('promotion_id', 'product_id')
    promotion = fk(Promotion)
    product = fk(Product)

    class Meta:
        db_table = 'promotion_products'


class Coupon(Operational):
    promotion = fk(Promotion)
    code = text(80)
    usage_limit = models.IntegerField(null=True)
    per_user_limit = models.IntegerField(null=True)

    class Meta:
        db_table = 'coupons'
        constraints = [models.UniqueConstraint(Upper('code'), name='coupon_code_ci_uq'), ck('limits', (Q(usage_limit__isnull=True) | Q(usage_limit__gt=0)) & (Q(per_user_limit__isnull=True) | Q(per_user_limit__gt=0)))]


class Cart(Operational):
    user = fk(User)
    status = text(16, default='active', db_default='active')
    expires_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'carts'
        constraints = [models.UniqueConstraint(fields=['user'], condition=Q(status='active'), name='cart_active_user_uq'), enum('status', 'active converted expired abandoned')]


class CartItem(Operational):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = fk(Product)
    added_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'cart_items'
        constraints = [uq('cart', 'product')]


class Order(Operational):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True)
    order_number = text(32, unique=True)
    user = fk(User)
    status = text(24, default='pending', db_default='pending')
    subtotal = money()
    discount_total = money(default=0, db_default=0)
    payable_total = money()
    currency = text(3, default='IRR', db_default='IRR')
    coupon = fk(Coupon, null=True)
    paid_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'orders'
        constraints = [enum('status', 'pending paid cancelled expired'), ck('amounts', Q(subtotal__gte=0, discount_total__gte=0, payable_total__gte=0, payable_total=F('subtotal')-F('discount_total'))), ck('currency', Q(currency='IRR')), ck('paid_time', ~Q(status='paid') | Q(paid_at__isnull=False))]
        indexes = [models.Index(fields=['user', '-created_at']), models.Index(fields=['status', 'created_at'])]


class OrderItem(Operational):
    order = fk(Order)
    product = fk(Product)
    product_title = text(255)
    product_kind = text(16)
    unit_price = money()
    discount_amount = money(default=0, db_default=0)
    final_amount = money()

    class Meta:
        db_table = 'order_items'
        constraints = [uq('order', 'product'), uq('id', 'order'), enum('product_kind', 'course pattern bundle'), ck('amounts', Q(unit_price__gte=0, discount_amount__gte=0, final_amount__gte=0, final_amount=F('unit_price')-F('discount_amount')))]


class BundlePurchaseSnapshot(models.Model):
    id = models.BigAutoField(primary_key=True)
    order_item = fk(OrderItem)
    product = fk(Product)
    product_title = text(255)
    product_kind = text(16)
    position = models.IntegerField()
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'bundle_purchase_snapshots'
        constraints = [uq('order_item', 'product'), uq('order_item', 'position'), enum('product_kind', 'course pattern'), ck('position_positive', Q(position__gte=0))]


class OrderDiscount(Operational):
    order = fk(Order)
    order_item = fk(OrderItem, null=True)
    promotion = fk(Promotion, null=True)
    code_snapshot = text(80, null=True)
    description = text(255)
    amount = money()

    class Meta:
        db_table = 'order_discounts'
        constraints = [ck('positive', Q(amount__gt=0))]


class CouponRedemption(Operational):
    coupon = fk(Coupon)
    user = fk(User)
    order = models.OneToOneField(Order, on_delete=models.PROTECT)
    redeemed_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'coupon_redemptions'
        constraints = [uq('coupon', 'order')]


class PaymentAttempt(Operational):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True)
    order = fk(Order)
    provider = text(32)
    authority = text(255, null=True)
    reference = text(255, null=True)
    amount = money()
    status = text(24, default='initiated', db_default='initiated')
    idempotency_key = text(128, unique=True)
    verified_at = models.DateTimeField(null=True)
    failure_code = text(80, null=True)

    class Meta:
        db_table = 'payment_attempts'
        constraints = [enum('status', 'initiated pending succeeded failed cancelled'), ck('positive', Q(amount__gte=0)), ck('verified', ~Q(status='succeeded') | Q(verified_at__isnull=False)), models.UniqueConstraint(fields=['provider', 'authority'], condition=Q(authority__isnull=False), name='payment_provider_authority_uq'), models.UniqueConstraint(fields=['provider', 'reference'], condition=Q(reference__isnull=False), name='payment_provider_reference_uq')]
        indexes = [models.Index(fields=['order', '-created_at'])]


class PaymentEvent(models.Model):
    payment = fk(PaymentAttempt)
    event_key = text(255)
    event_type = text(40)
    payload = models.JSONField(default=dict, db_default={})
    received_at = models.DateTimeField(db_default=Now())
    processed_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'payment_events'
        constraints = [uq('payment', 'event_key')]


class Refund(Operational):
    payment = fk(PaymentAttempt)
    amount = money()
    status = text(20, default='requested', db_default='requested')
    provider_ref = text(255, null=True)
    reason = models.TextField(default='', db_default='')
    requested_by = fk(User, null=True, related_name='+', db_column='requested_by')
    approved_by = fk(User, null=True, related_name='+', db_column='approved_by')
    completed_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'refunds'
        constraints = [enum('status', 'requested approved processing completed failed rejected'), ck('positive', Q(amount__gt=0)), ck('completed_time', ~Q(status='completed') | Q(completed_at__isnull=False)), models.UniqueConstraint(fields=['provider_ref'], condition=Q(provider_ref__isnull=False), name='refund_provider_ref_uq')]


class RefundItem(Operational):
    refund = fk(Refund)
    order_item = fk(OrderItem)
    amount = money()

    class Meta:
        db_table = 'refund_items'
        constraints = [uq('refund', 'order_item'), ck('positive', Q(amount__gt=0))]


class IdempotencyKey(Operational):
    scope = text(60)
    key = text(128)
    request_hash = text(64)
    resource_type = text(40, null=True)
    resource_id = models.BigIntegerField(null=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'idempotency_keys'
        constraints = [uq('scope', 'key')]


class Entitlement(Operational):
    user = fk(User)
    product = fk(Product)
    status = text(16, default='active', db_default='active')
    granted_at = models.DateTimeField(db_default=Now())
    revoked_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'entitlements'
        constraints = [uq('user', 'product'), enum('status', 'active revoked')]
        indexes = [models.Index(fields=['user', 'status'])]


class EntitlementGrant(models.Model):
    entitlement = fk(Entitlement)
    order_item = fk(OrderItem, null=True)
    grant_type = text(20)
    granted_by = fk(User, null=True, db_column='granted_by')
    status = text(16, default='active', db_default='active')
    created_at = models.DateTimeField(db_default=Now())
    revoked_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'entitlement_grants'
        constraints = [enum('grant_type', 'purchase manual'), enum('status', 'active revoked'), models.UniqueConstraint(fields=['entitlement', 'order_item'], condition=Q(order_item__isnull=False), name='entitlement_grant_purchase_uq'), ck('source', Q(grant_type='purchase', order_item__isnull=False) | Q(grant_type='manual', order_item__isnull=True, granted_by__isnull=False))]
        permissions = [('grant_manual_access', 'Grant audited manual access')]


class EntitlementEvent(models.Model):
    entitlement = fk(Entitlement)
    grant = fk(EntitlementGrant, null=True)
    actor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = text(24)
    reason = models.TextField(default='', db_default='')
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'entitlement_events'


class DownloadGrant(Operational):
    entitlement = fk(Entitlement)
    pattern_file = fk(PatternFile)
    token_hash = text(64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'download_grants'
        constraints = [ck('expiry', Q(expires_at__gt=F('created_at')))]


class LessonProgress(Operational):
    user = fk(User)
    lesson = fk(Lesson)
    last_position_seconds = models.IntegerField(default=0, db_default=0)
    completed_at = models.DateTimeField(null=True)
    last_watched_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'lesson_progress'
        constraints = [uq('user', 'lesson'), ck('position_positive', Q(last_position_seconds__gte=0))]


class Review(Operational):
    user = fk(User)
    product = fk(Product)
    rating = models.SmallIntegerField()
    title = text(200, null=True)
    body = models.TextField(default='', db_default='')
    status = text(20, default='pending', db_default='pending')
    moderated_by = fk(User, null=True, related_name='+', db_column='moderated_by')
    moderated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'reviews'
        constraints = [uq('user', 'product'), ck('rating_range', Q(rating__gte=1, rating__lte=5)), enum('status', 'pending approved rejected')]
        indexes = [models.Index(fields=['product', 'status', '-created_at'])]


class ReviewModeration(models.Model):
    review = fk(Review)
    moderator = fk(User)
    action = text(20)
    reason = models.TextField(default='', db_default='')
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'review_moderations'


class AuditLog(models.Model):
    actor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = text(100)
    entity_type = text(80)
    entity_id = text(80)
    before_data = models.JSONField(null=True)
    after_data = models.JSONField(null=True)
    request_id = models.UUIDField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'audit_logs'
        indexes = [models.Index(fields=['entity_type', 'entity_id', '-created_at']), models.Index(fields=['actor', '-created_at'])]
