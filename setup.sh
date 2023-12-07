#!/bin/bash

echo "1. Creating virtual environment..."
python -m venv env

echo "2. Activating virtual environment..."
source env/bin/activate

echo "3. Moving to the API"
cd mapi

echo "4. Installing dependencies..."
pip install -r requirements.txt

echo "4. Creating .env file..."
if [ ! -f .env ]; then
    echo "4. Creating .env file..."
    cp .env.example .env
else
    echo ".env file already exists. Skipping creation."
fi

echo "5. Running migrations..."
python manage.py migrate

echo "6. Starting the development server..."
python manage.py runserver
