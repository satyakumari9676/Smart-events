# Smart Event Management & Budget Prediction System

## 📌 Project Overview
The **Smart Event Management System** is a full-stack web application built using **Django** and **Machine Learning**. It not only allows users to browse and plan events but also uses an AI-driven approach (Random Forest) to predict and estimate the budget required for the event based on user inputs (guests, location, required services, etc.).

---

## 🚀 Key Features
- **User Authentication:** Secure signup, login, and session management.
- **Service Browsing:** Browse various event types like Weddings, Corporate Events, Birthdays, etc.
- **AI Budget Predictor:** Input your requirements (No. of guests, location type, specific sub-services like food, photography, etc.) to get an instant AI-predicted budget.
- **Dynamic Datasets:** Machine Learning models are trained on dynamic datasets for accurate real-time predictions.

---

## 🛠️ Technologies Used
- **Backend:** Python, Django
- **Machine Learning:** Scikit-Learn (Random Forest Regressor), Pandas, Joblib
- **Frontend:** HTML, CSS, JavaScript (Django Templates)
- **Database:** SQLite3

---

## 📂 Project Structure

```text
d:\event\event\event\
│
├── event_management/              # Main Django Web Application
│   ├── event_management/          # Core Django settings & configurations
│   ├── accounts/                  # User Authentication (Login/Signup/Passwords)
│   ├── budget/                    # ML Integration: Predicts budget using .pkl models
│   ├── pages/                     # Handles static web pages (Home, About, etc.)
│   ├── services/                  # Manages event services listing
│   ├── event_services/            # Core event logic and bookings
│   ├── careers/                   # Careers/Jobs page module
│   ├── templates/                 # Global HTML templates for the frontend
│   ├── static/                    # CSS, JS, and Image files
│   ├── media/                     # User-uploaded media files
│   ├── db.sqlite3                 # Local SQLite Database
│   └── manage.py                  # Django command-line tool
│
├── models/                        # Contains Trained Machine Learning Models
│   ├── wedding_budget_model.pkl   # Saved Random Forest models
│   ├── corporate_budget_model.pkl
│   └── *_features.txt             # Saved feature sequence for accurate prediction
│
├── datasets (*.csv)               # Raw datasets used for training models
│   ├── wedding_dataset.csv
│   ├── corporate_event_dataset.csv
│   └── ...
│
├── generate_dataset.py            # Python script to generate/clean CSV datasets
├── train_models.py                # Script to train ML models and save them to /models/
└── requirements.txt               # List of all Python dependencies required
```

---

## ⚙️ How It Works (Workflow)

1. **Data Preparation:** 
   The `generate_dataset.py` prepares historical data of event costs.
2. **Model Training:** 
   Running `train_models.py` trains the **Random Forest** algorithm on the datasets and saves the learned models inside the `models/` folder as `.pkl` files.
3. **User Interaction:** 
   The user visits the web app, logs in via the `accounts` app, and selects an event type.
4. **Prediction:** 
   The user fills out an event requirement form. The `budget` app intercepts this data, loads the respective `.pkl` model, and instantly predicts the total estimated budget.

---

## 💻 How to Run the Project Locally

### 1. Install Dependencies
Make sure you have Python installed. Run the following command to install the required libraries:
```bash
pip install -r requirements.txt
```

### 2. Train the Machine Learning Models (Optional if models exist)
If the `models/` directory is empty, you need to train the models first:
```bash
python train_models.py
```

### 3. Run the Django Server
Navigate to the Django project folder:
```bash
cd event_management
```
Apply migrations (if any) and start the server:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 4. Open in Browser
Visit `http://128.0.0.1:8000/` in your web browser.

---
