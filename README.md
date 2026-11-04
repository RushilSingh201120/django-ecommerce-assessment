# Django eCommerce Management System

## Project Overview

This project is a Django-based eCommerce Management System developed as part of the HyperionDev assessment. It supports buyers and vendors, store and product management, shopping cart functionality, order processing, reviews, and a REST API.

## Features

- Buyer and vendor registration and authentication.
- Vendor store and product management.
- Product browsing and search.
- Session-based shopping cart and checkout.
- Order history and email notifications.
- Product reviews, including verified and unverified reviews.
- REST API endpoints for stores, products, and reviews.
- Authentication and permission checks for API operations.
- Reddit API integration.

## Technologies

- Python
- Django
- Django REST Framework
- MariaDB 
- Requests
- HTML and CSS

## Installation and Setup

### 1. Clone the repository

Clone this repository from your personal GitHub account, then navigate into the project folder.


git clone https://github.com/RushilSingh201120/django-ecommerce-assessment.git
cd django-ecommerce-assessment


Replace the placeholder URL with this repository's actual GitHub URL.

### 2. Create and activate a virtual environment

On Windows:


python -m venv myenv
myenv\Scripts\activate


### 3. Install dependencies


pip install -r requirements.txt


### 4. Configure environment variables

Copy the root-level `.env.example` file and name the copy `.env`. Fill in your own local values for the Django secret key, database credentials, and email credentials.



### 5. Configure the database

Install and start MariaDB. Create the database and database user specified in your `.env` file, and ensure the credentials match your Django settings.

### 6. Apply database migrations


python manage.py migrate


### 7. Run the development server


python manage.py runserver


Open `http://127.0.0.1:8000/` in your browser.

## API Endpoints

- `/api/stores/` — store API.
- `/api/stores/<store_id>/products/` — products belonging to a store.
- `/api/reviews/` — review API.

The available HTTP methods and permissions depend on the endpoint and authentication status.

## Security

Environment files containing real credentials are excluded from version control. API write operations use authentication and permission checks where configured.

## Notes

Configure your own database and email credentials before running it locally.
