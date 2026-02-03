# tournament_poker_bankroll_manager
Django poker bankroll management application with tournament tracking and analytics. Tracking your most basic tournament recap information like: Avg Buy-ins, ROI%, ITM%, $/hour rate and many more:)

Features
User Authentication - Custom user model with bankroll tracking

Tournament Management - Log buy-ins, cashes, and results

Bankroll Tracking - Real-time bankroll updates with adjustments

Performance Analytics - ROI, ROI BB, average buy-in, and profit/loss statistics

Secure & Professional - PostgreSQL database with environment-based configuration

Tech Stack
Backend: Django 6.0, Python 3.12+

Database: PostgreSQL (production), SQLite (development option)

Security: Environment variables, Django authentication

Frontend: Bootstrap 5, Django Templates

Deployment: Ready for Heroku/Railway/DigitalOcean

Prerequisites
Python 3.12 or higher

PostgreSQL 14+ (recommended) or SQLite

Git

Installation
1. Clone the Repository
bash
git clone https://github.com/Kaloyan19/tournament_poker_bankroll_manager.git
cd tournament_poker_bankroll_manager
2. Create Virtual Environment
bash
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the project root:

bash
# Database Configuration
DB_NAME=poker_bankroll
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Generate a secret key with: 
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
5. Set Up PostgreSQL Database
sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE poker_bankroll;

-- Exit
\q
6. Run Migrations
bash
python manage.py migrate
7. Create Superuser
bash
python manage.py createsuperuser
8. Run Development Server
bash
python manage.py runserver
Visit http://localhost:8000 in your browser!