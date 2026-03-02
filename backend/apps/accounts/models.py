from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Extended User model for finance app"""
    
    CURRENCY_CHOICES = (
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('JPY', 'Japanese Yen'),
        ('INR', 'Indian Rupee'),
    )
    
    TIMEZONE_CHOICES = (
        ('UTC', 'UTC'),
        ('US/Eastern', 'Eastern Time'),
        ('US/Central', 'Central Time'),
        ('US/Mountain', 'Mountain Time'),
        ('US/Pacific', 'Pacific Time'),
        ('Europe/London', 'London'),
        ('Europe/Paris', 'Paris'),
        ('Asia/Tokyo', 'Tokyo'),
        ('Asia/Dubai', 'Dubai'),
    )
    
    # Profile
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Preferences
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Financial Profile
    annual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ('conservative', 'Conservative'),
            ('moderate', 'Moderate'),
            ('aggressive', 'Aggressive'),
        ],
        default='moderate'
    )
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    plaid_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Privacy & Notifications
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['plaid_user_id']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_total_balance(self):
        """Get total balance across all accounts"""
        return sum(account.balance for account in self.accounts.all())


class BankAccount(models.Model):
    """User's connected bank accounts via Plaid"""
    
    ACCOUNT_TYPE_CHOICES = (
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('investment', 'Investment'),
        ('credit', 'Credit Card'),
        ('loan', 'Loan'),
        ('mortgage', 'Mortgage'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(
        User,
        related_name='accounts',
        on_delete=models.CASCADE
    )
    
    # Plaid Integration
    plaid_account_id = models.CharField(max_length=255, unique=True)
    plaid_access_token = models.CharField(max_length=500)
    plaid_item_id = models.CharField(max_length=255)
    
    # Account Information
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    institution_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, blank=True)  # Last 4 digits
    routing_number = models.CharField(max_length=50, blank=True)
    
    # Balance Information
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    is_active = models.BooleanField(default=True)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('syncing', 'Syncing'),
            ('synced', 'Synced'),
            ('error', 'Error'),
            ('disconnected', 'Disconnected'),
        ],
        default='synced'
    )
    
    # Sync Information
    last_sync = models.DateTimeField(null=True, blank=True)
    last_transaction_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-connected_at']
        unique_together = ('user', 'plaid_account_id')
    
    def __str__(self):
        return f"{self.account_name} ({self.account_type})"


class TransactionCategory(models.Model):
    """Transaction categories"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Font Awesome or emoji
    color = models.CharField(max_length=7, default='#3B82F6')
    
    # Budget tracking
    is_income = models.BooleanField(default=False)
    is_essential = models.BooleanField(default=False)
    
    # ML/Categorization
    keywords = models.JSONField(default=list, blank=True)  # Keywords for matching
    
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = "Transaction Categories"
    
    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Bank transactions"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(
        User,
        related_name='transactions',
        on_delete=models.CASCADE
    )
    
    account = models.ForeignKey(
        BankAccount,
        related_name='transactions',
        on_delete=models.CASCADE
    )
    
    # Transaction Data
    plaid_transaction_id = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=500)
    merchant_name = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Transaction Details
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('debit', 'Debit'),
            ('credit', 'Credit'),
        ]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='posted')
    
    # Categorization
    category = models.ForeignKey(
        TransactionCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='transactions'
    )
    is_manually_categorized = models.BooleanField(default=False)
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Recurring
    is_recurring = models.BooleanField(default=False)
    recurring_pattern = models.CharField(
        max_length=50,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
        ],
        null=True,
        blank=True
    )
    
    # Dates
    transaction_date = models.DateField(db_index=True)
    posted_date = models.DateField(null=True, blank=True)
    
    # AI Detection
    is_anomaly = models.BooleanField(default=False)
    anomaly_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user', '-transaction_date']),
            models.Index(fields=['category']),
            models.Index(fields=['merchant_name']),
            models.Index(fields=['is_recurring']),
            models.Index(fields=['is_anomaly']),
        ]
    
    def __str__(self):
        return f"{self.merchant_name} - ${self.amount} ({self.transaction_date})"
    
    def get_month_year(self):
        return self.transaction_date.strftime('%Y-%m')


class Budget(models.Model):
    """Budget tracking for categories"""
    
    PERIOD_CHOICES = (
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )
    
    user = models.ForeignKey(
        User,
        related_name='budgets',
        on_delete=models.CASCADE
    )
    
    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    
    # Budget Details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    
    # Alert Threshold
    alert_threshold = models.IntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Alert when spending reaches this % of budget"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Tracking
    current_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'category', 'period_start', 'period_end')
    
    def __str__(self):
        return f"{self.category.name} Budget - ${self.amount}/{self.period}"
    
    def get_percentage_spent(self):
        if self.amount == 0:
            return 0
        return (float(self.current_spent) / float(self.amount)) * 100
    
    def is_over_budget(self):
        return self.current_spent > self.amount
    
    def should_alert(self):
        return self.get_percentage_spent() >= self.alert_threshold


class SavingsGoal(models.Model):
    """Savings goals for users"""
    
    user = models.ForeignKey(
        User,
        related_name='savings_goals',
        on_delete=models.CASCADE
    )
    
    # Goal Details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    
    # Financial Details
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Timeline
    target_date = models.DateField(null=True, blank=True)
    monthly_contribution = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_percentage_complete(self):
        if self.target_amount == 0:
            return 0
        return (float(self.current_amount) / float(self.target_amount)) * 100
    
    def is_completed(self):
        return self.current_amount >= self.target_amount
    
    def get_remaining_amount(self):
        return max(0, self.target_amount - self.current_amount)


class FinancialInsight(models.Model):
    """AI-generated financial insights"""
    
    INSIGHT_TYPE_CHOICES = (
        ('spending_pattern', 'Spending Pattern'),
        ('saving_opportunity', 'Saving Opportunity'),
        ('category_analysis', 'Category Analysis'),
        ('trend', 'Trend'),
        ('anomaly', 'Anomaly'),
        ('recommendation', 'Recommendation'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    user = models.ForeignKey(
        User,
        related_name='insights',
        on_delete=models.CASCADE
    )
    
    # Insight Details
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Analysis
    category = models.ForeignKey(
        TransactionCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    data = models.JSONField(default=dict, blank=True)  # Raw analysis data
    
    # Impact
    potential_savings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Timestamps
    generated_at = models.DateTimeField(auto_now_add=True)
    period = models.CharField(max_length=20, blank=True)  # e.g., "2024-01"
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['user', '-generated_at']),
            models.Index(fields=['insight_type']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"


class TransactionCategorization(models.Model):
    """Track ML categorization history"""
    
    transaction = models.OneToOneField(
        Transaction,
        related_name='categorization_record',
        on_delete=models.CASCADE
    )
    
    # ML Prediction
    predicted_category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='predictions'
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # User Feedback
    user_corrected = models.BooleanField(default=False)
    corrected_at = models.DateTimeField(null=True, blank=True)
    
    # Model Info
    model_version = models.CharField(max_length=50)
    features_used = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Categorization for {self.transaction.merchant_name}"
