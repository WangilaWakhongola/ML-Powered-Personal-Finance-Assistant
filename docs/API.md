# ML Finance Assistant - API Documentation

## Base URL

- Development: `http://localhost:8000/api`
- Production: `https://api.mlfinanceassistant.com/api`

## Authentication

All endpoints (except auth) require JWT token:

```
Authorization: Bearer <access_token>
```

### Register

**Endpoint:** `POST /auth/register/`

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Login

**Endpoint:** `POST /auth/login/`

```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAi...",
  "refresh": "eyJ0eXAi..."
}
```

### Refresh Token

**Endpoint:** `POST /auth/refresh/`

```json
{
  "refresh": "eyJ0eXAi..."
}
```

---

## Bank Accounts (Plaid Integration)

### Connect Bank Account

**Endpoint:** `POST /accounts/connect-plaid/`

```json
{
  "public_token": "public-...",
  "metadata": {
    "institution": {"institution_id": "...", "name": "..."},
    "accounts": [{"id": "...", "name": "..."}]
  }
}
```

**Response:**
```json
{
  "id": 1,
  "account_name": "Chase Checking",
  "account_type": "checking",
  "institution_name": "Chase Bank",
  "current_balance": 5000.00,
  "currency": "USD",
  "is_active": true,
  "connected_at": "2024-01-15T10:30:00Z"
}
```

### List Bank Accounts

**Endpoint:** `GET /accounts/`

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "account_name": "Chase Checking",
      "current_balance": 5000.00,
      "institution_name": "Chase Bank",
      "last_sync": "2024-01-18T15:00:00Z"
    }
  ]
}
```

### Disconnect Account

**Endpoint:** `DELETE /accounts/{id}/`

### Sync Transactions

**Endpoint:** `POST /accounts/{id}/sync/`

**Response:**
```json
{
  "status": "syncing",
  "transactions_synced": 150,
  "last_sync": "2024-01-18T15:00:00Z"
}
```

---

## Transactions

### List Transactions

**Endpoint:** `GET /transactions/`

**Query Parameters:**
- `account`: Filter by account ID
- `category`: Filter by category
- `start_date`: From date (YYYY-MM-DD)
- `end_date`: To date (YYYY-MM-DD)
- `is_recurring`: Filter recurring transactions
- `page`: Page number

**Response:**
```json
{
  "count": 250,
  "next": "http://localhost:8000/api/transactions/?page=2",
  "results": [
    {
      "id": 1,
      "merchant_name": "Starbucks",
      "description": "Starbucks - Coffee",
      "amount": 5.50,
      "category": "Food & Dining",
      "transaction_date": "2024-01-18",
      "is_recurring": true,
      "is_anomaly": false,
      "anomaly_score": 0.05
    }
  ]
}
```

### Get Transaction Details

**Endpoint:** `GET /transactions/{id}/`

### Update Transaction Category

**Endpoint:** `PATCH /transactions/{id}/`

```json
{
  "category": "Shopping"
}
```

### Bulk Categorize Transactions

**Endpoint:** `POST /transactions/categorize-batch/`

```json
{
  "transaction_ids": [1, 2, 3, 4, 5]
}
```

---

## Insights & Analytics

### Get Financial Summary

**Endpoint:** `GET /insights/summary/`

**Query Parameters:**
- `period`: month, quarter, year

**Response:**
```json
{
  "period": "2024-01",
  "total_income": 5000.00,
  "total_expenses": 2500.00,
  "net_savings": 2500.00,
  "spending_by_category": {
    "Food & Dining": 500.00,
    "Transportation": 300.00,
    "Shopping": 800.00,
    "Utilities": 250.00
  },
  "top_merchants": [
    {"name": "Whole Foods", "total": 350.00},
    {"name": "Uber", "total": 200.00}
  ]
}
```

### Get Spending Trends

**Endpoint:** `GET /insights/trends/`

**Response:**
```json
{
  "daily_totals": [100, 150, 120, ...],
  "category_trends": {
    "Food & Dining": [300, 350, 280, ...],
    "Transportation": [150, 200, 180, ...]
  },
  "trend_analysis": {
    "increasing_categories": ["Shopping"],
    "decreasing_categories": ["Food & Dining"],
    "stable_categories": ["Utilities"]
  }
}
```

### Get Spending Predictions

**Endpoint:** `GET /insights/predictions/`

**Query Parameters:**
- `days_ahead`: Number of days to predict (default: 30)

**Response:**
```json
{
  "total_predictions": [100, 120, 115, ...],
  "by_category": {
    "Food & Dining": [300, 320, 310, ...],
    "Transportation": [150, 160, 155, ...]
  },
  "average_daily": 125.50,
  "forecast_confidence": 0.85,
  "forecast_horizon": 30
}
```

### Get AI Recommendations

**Endpoint:** `GET /insights/recommendations/`

**Response:**
```json
{
  "recommendations": [
    {
      "id": 1,
      "title": "Reduce food spending",
      "description": "Your food spending increased by 30% this month",
      "potential_savings": 150.00,
      "priority": "high"
    },
    {
      "id": 2,
      "title": "Optimize subscriptions",
      "description": "You have 3 inactive subscriptions",
      "potential_savings": 45.00,
      "priority": "medium"
    }
  ]
}
```

### Get Anomalies

**Endpoint:** `GET /insights/anomalies/`

**Response:**
```json
{
  "anomalies": [
    {
      "transaction_id": 1,
      "merchant": "Apple Inc",
      "amount": 999.00,
      "reason": "Amount is 5x higher than typical",
      "anomaly_score": 0.95
    }
  ]
}
```

---

## Budgets

### Create Budget

**Endpoint:** `POST /budgets/`

```json
{
  "category": "Food & Dining",
  "amount": 500.00,
  "period": "monthly",
  "alert_threshold": 80
}
```

### List Budgets

**Endpoint:** `GET /budgets/`

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "category": "Food & Dining",
      "amount": 500.00,
      "current_spent": 350.00,
      "period": "monthly",
      "percentage_spent": 70.0,
      "is_over_budget": false
    }
  ]
}
```

### Update Budget

**Endpoint:** `PUT /budgets/{id}/`

```json
{
  "amount": 600.00,
  "alert_threshold": 75
}
```

### Delete Budget

**Endpoint:** `DELETE /budgets/{id}/`

---

## Savings Goals

### Create Goal

**Endpoint:** `POST /savings-goals/`

```json
{
  "name": "Vacation",
  "target_amount": 3000.00,
  "target_date": "2024-12-31",
  "monthly_contribution": 250.00
}
```

### List Goals

**Endpoint:** `GET /savings-goals/`

### Update Goal

**Endpoint:** `PUT /savings-goals/{id}/`

### Add Contribution

**Endpoint:** `POST /savings-goals/{id}/contribute/`

```json
{
  "amount": 250.00
}
```

---

## AI Chat Assistant

### Send Message

**Endpoint:** `POST /ai/chat/`

```json
{
  "message": "How much did I spend on food this month?"
}
```

**Response:**
```json
{
  "id": 1,
  "message": "How much did I spend on food this month?",
  "response": "You spent $450 on food and dining in January 2024, which is 20% higher than December.",
  "sources": [
    {"type": "spending_data", "data": {"total": 450, "category": "Food & Dining"}}
  ],
  "created_at": "2024-01-18T15:30:00Z"
}
```

### Get Chat History

**Endpoint:** `GET /ai/chat/history/`

---

## Categories

### List Categories

**Endpoint:** `GET /categories/`

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Food & Dining",
      "slug": "food-dining",
      "icon": "utensils",
      "color": "#FF6B6B",
      "is_income": false,
      "is_essential": true
    }
  ]
}
```

---

## Error Responses

```json
{
  "error": "Error message",
  "status_code": 400,
  "details": {
    "field": ["Error message"]
  }
}
```

### Common Status Codes

- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Server Error

---

## Rate Limiting

- **Limit**: 1000 requests/hour per user
- **Headers**:
  - `X-RateLimit-Limit`: 1000
  - `X-RateLimit-Remaining`: 999
  - `X-RateLimit-Reset`: Unix timestamp

---

## Pagination

List endpoints support pagination:

```
GET /transactions/?page=2&page_size=50
```

---

For more details, see [Full API Documentation](http://localhost:8000/api/schema/swagger/)
