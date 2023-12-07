# Mezanmi API

Welcome to Mezanmi API! This guide will help you set up and run the project locally.

## Prerequisites

you can find all the dependencies inside the `requirements.txt` file

## Getting Started #1

 - `git clone https://github.com/lemayzeur/mezanmi.git`
 - `cd mezanmi`
 - `./setup.sh`

Alternatively, you have the option to perform this task manually after cloning the repository.

## Getting Started #2

 - `git clone https://github.com/lemayzeur/mezanmi.git`
 - `cd mezanmi`

1. Create a virtual environment:

```python -m venv env```

2. Activate the virtual environment:

 - On Windows:

      ```.\env\Scripts\activate```

 - On macOS/Linux:

      ```source env/bin/activate```

3. Install project dependencies:

```pip install -r requirements.txt```

4. Create a copy of the `.env.example` file and rename it to `.env`:

```cp .env.example .env```

Update the values in `.env` as needed.

5. Run database migrations:

```python manage.py migrate```

6. Start the development server:

```python manage.py runserver```

Your project will be accessible at `http://localhost:8000/`
