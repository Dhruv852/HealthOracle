# HealthOracle

HealthOracle is a Django-based web application that leverages machine learning to provide predictive health risk assessments for heart disease, lung disease, liver disease, and diabetes. It also features a smart health chatbot powered by Gemini AI to offer actionable health advice and answer user queries.

## Features

- **User Authentication & Profiles**: Secure registration, login, and personalized patient profiles.
- **Predictive Health Tests**: ML-powered risk predictions for:
  - Heart Disease
  - Lung Disease
  - Liver Disease
  - Diabetes
- **Prediction History**: View and manage your past predictions and advice.
- **AI Health Chatbot**: Ask health-related questions or get tailored advice based on your test results using Gemini AI.
- **Actionable Health Suggestions**: Receive specific, evidence-based recommendations after each test.
- **Modern UI**: Responsive design with Bootstrap 5 and crispy forms.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/healthoracle.git
cd healthoracle
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py migrate
```

### 5. (Optional) Train ML Models
If you want to retrain the models, run:
```bash
python train_models.py
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Usage
- Register or log in to your account.
- Complete your profile for personalized results.
- Select a health test, fill in the required details, and submit.
- View your risk assessment, category, and actionable advice.
- Access your prediction history at any time.
- Use the chatbot for health questions or to get more advice based on your results.

## File Structure
- `HealthOracle/` - Main Django app (ML logic, views, settings)
- `users/` - User management app
- `static/` and `templates/` - Frontend assets and HTML templates
- `*.h5`, `*.pkl` - Pre-trained ML models and scalers
- `requirements.txt` - Python dependencies

## Notes
- **Database**: Uses SQLite by default (`db.sqlite3`).
- **Sensitive Files**: Do not commit `db.sqlite3`, `__pycache__/`, or any API keys to public repos.
- **ML Models**: Pre-trained models are included. Retrain only if needed.
- **Gemini API**: Requires a valid Gemini API key for chatbot features (set in `HealthOracle/settings.py`).

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
Specify your license here (e.g., MIT, Apache 2.0, etc.). 








## update added for version control demonstration 

added docker 

# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port (for local testing, most PaaS set $PORT)
EXPOSE 8000

# Start server
CMD gunicorn HealthOracle.wsgi:application --bind 0.0.0.0:${PORT:-8000} 