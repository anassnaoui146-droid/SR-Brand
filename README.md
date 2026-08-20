# Python + MySQL backend

## 1) Create the database
Open phpMyAdmin or MySQL and import:

`schema.sql`

This creates `divastra_db` plus products, users, orders, order_items, newsletter and contact_messages.

## 2) Install Python dependencies

```bash
cd backend_python
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

For macOS/Linux activation:

```bash
source .venv/bin/activate
```

## 3) Configure MySQL

Copy `.env.example` values into your environment. The defaults expect a local MySQL server with:

- host: `127.0.0.1`
- port: `3306`
- user: `root`
- password: empty
- database: `divastra_db`

Windows PowerShell example:

```powershell
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD=""
$env:MYSQL_DATABASE="divastra_db"
```

## 4) Start the API

```bash
python app.py
```

API: `http://127.0.0.1:5000/api`

Important endpoints:

- `GET /api/health`
- `GET /api/products`
- `POST /api/products`
- `POST /api/orders`
- `GET /api/orders`
- `POST /api/newsletter`

The checkout in the website sends the order to `/api/orders`, stores it in MySQL and then notifies the Java service.
