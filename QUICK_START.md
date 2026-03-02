# 🚀 Quick Start - ML Finance Assistant

## 30-Second Setup

```bash
# 1. Clone
git clone <repo-url>
cd ml-finance-assistant

# 2. Setup
cp .env.example .env
# Edit .env with Plaid credentials

# 3. Run
docker-compose up --build

# 4. Create superuser (new terminal)
docker-compose exec backend python manage.py createsuperuser

# Done! 🎉
```

## Access Points

| Service | URL |
|---------|-----|
| **Web App** | http://localhost:3000 |
| **Backend API** | http://localhost:8000/api/ |
| **API Docs** | http://localhost:8000/api/schema/swagger/ |
| **Admin** | http://localhost:8000/admin/ |

## Essential Commands

```bash
# Start services
make up

# Run tests
make test

# View logs
make logs-backend

# Database
make migrate
make db-reset

# Code quality
make lint
make format
```

## Key Features

✅ Bank account connection (Plaid)  
✅ Automatic transaction categorization  
✅ Spending predictions  
✅ AI-powered insights  
✅ Budget tracking  
✅ Web + Mobile apps  

## What's Inside

- **Backend**: Django REST API + ML models
- **Frontend**: React web app
- **Mobile**: React Native with Expo
- **ML**: Expense categorizer + Spending predictor
- **Database**: PostgreSQL + Redis
- **DevOps**: Docker, Celery, CI/CD

## Next Steps

1. ✅ Get Plaid credentials
2. ✅ Update .env
3. ✅ Run `docker-compose up`
4. ✅ Create superuser
5. ✅ Visit http://localhost:3000

## Troubleshooting

**Port in use?**
```bash
make down
make up
```

**Database error?**
```bash
make db-reset
```

**Build issues?**
```bash
docker-compose down -v
docker-compose up --build
```

## Documentation

- [Full Setup Guide](./docs/SETUP.md)
- [API Documentation](./docs/API.md)
- [ML Models Guide](./docs/ML_MODELS.md)

## Support

- 📧 Email: support@mlfinanceassistant.com
- 🐛 GitHub Issues
- 💬 Discussions

---

**Happy coding!** 💰🤖
