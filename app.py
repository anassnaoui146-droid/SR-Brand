from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from decimal import Decimal
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import mysql.connector
from mysql.connector import Error

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(__name__)
CORS(app)
DB_CONFIG = {
    'host': 'bok0ypbful2dko8erxl3-mysql.services.clever-cloud.com',
    'port': 3306,
    'user': 'uujgrsx3mjllh7g5',
    'password': 'Z902Hx8J6xq37KmWUh8e',
    'database': 'bok0ypbful2dko8erxl3'
}
JAVA_ORDER_URL = os.getenv('JAVA_ORDER_URL', 'http://127.0.0.1:8080/api/java/order')

DEFAULT_CATEGORIES = ['Robes', 'Ensembles', 'Accessoires', 'Nouveautés']
DEFAULT_PRODUCTS = [
    ('Ensemble Premium', 'ensembles', 299.00, 599.00, 'BEST SELLER', 'Décrivez ici votre produit.', 'S,M,L,XL', '', 20, 1),
    ('Robe Signature', 'robes', 249.00, 399.00, 'NOUVEAU', 'Ajoutez votre description produit.', 'S,M,L', '', 20, 1),
    ('Ensemble Satin', 'ensembles', 319.00, 450.00, '-29%', 'Ajoutez votre description produit.', 'S,M,L,XL', '', 15, 0),
    ('Sac Minimal', 'accessoires', 179.00, 229.00, 'ÉDITION', 'Ajoutez votre description produit.', 'Unique', '', 10, 0),
    ('Robe Élégance', 'robes', 289.00, 399.00, 'TENDANCE', 'Ajoutez votre description produit.', 'S,M,L', '', 12, 1),
    ('Ensemble City', 'ensembles', 279.00, 359.00, 'NOUVEAU', 'Ajoutez votre description produit.', 'S,M,L,XL', '', 14, 0),
    ('Lunettes Chic', 'accessoires', 149.00, 199.00, '', 'Ajoutez votre description produit.', 'Unique', '', 8, 0),
    ('Robe Soirée', 'robes', 349.00, 499.00, 'LIMITÉ', 'Ajoutez votre description produit.', 'S,M,L,XL', '', 6, 1),
]


def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def product_dict(row):
    row = dict(row)
    row['price'] = json_safe(row['price'])
    row['oldPrice'] = json_safe(row.pop('old_price', None))
    row['sizes'] = row.pop('sizes', '').split(',') if row.get('sizes') else []
    row['stock'] = int(row.get('stock', 0))
    row['featured'] = bool(row.get('featured', 0))
    return row


def init_database():
    # Database must be created once via mysql_schema.sql because MySQL
    # does not permit selecting a missing database through the app connection.
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    for name in DEFAULT_CATEGORIES:
        cur.execute('INSERT IGNORE INTO categories (name) VALUES (%s)', (name,))

    cur.execute('SELECT COUNT(*) AS total FROM products')
    if cur.fetchone()['total'] == 0:
        for item in DEFAULT_PRODUCTS:
            name, category, price, old_price, badge, description, sizes, image, stock, featured = item
            cur.execute('''
                INSERT INTO products
                    (category, name, price, old_price, badge, description, sizes, image, stock, featured)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ''', (category, name, price, old_price, badge, description, sizes, image, stock, featured))
    conn.commit()
    cur.close()
    conn.close()



@app.get('/api/health')
def health():
    try:
        conn = get_conn()
        conn.close()
        return jsonify({'ok': True, 'service': 'python-store-api', 'mysql': True})
    except Error as exc:
        return jsonify({'ok': False, 'service': 'python-store-api', 'mysql': False, 'error': str(exc)}), 503


@app.get('/api/products')
def products():
    category = request.args.get('category', 'all').strip().lower()
    q = request.args.get('q', '').strip()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    sql = '''
        SELECT id, name, category, price, old_price, badge,
               description, sizes, image, stock, featured
        FROM products
        WHERE 1=1
    '''
    params = []
    if category != 'all':
        sql += ' AND category = %s'
        params.append(category)
    if q:
        sql += ' AND (name LIKE %s OR description LIKE %s)'
        like = f'%{q}%'
        params.extend([like, like])
    sql += ' ORDER BY featured DESC, id DESC'
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([product_dict(r) for r in rows])


@app.post('/api/products')
def create_product():
    data = request.get_json(silent=True) or {}
    required = ['name', 'category', 'price']
    if any(k not in data for k in required):
        return jsonify({'error': 'name, category and price are required'}), 400

    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute('''
        INSERT INTO products
            (name, category, price, old_price, badge, description, sizes, image, stock, featured)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ''', (
        data['name'], data['category'], data['price'], data.get('old_price'),
        data.get('badge', ''), data.get('description', ''), ','.join(data.get('sizes', [])),
        data.get('image', ''), data.get('stock', 0), int(bool(data.get('featured', False)))
    ))
    new_id = cur.lastrowid
    conn.commit()
    cur.execute('SELECT * FROM products WHERE id=%s', (new_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(product_dict(row)), 201


@app.post('/api/newsletter')
def newsletter():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    if not email or '@' not in email:
        return jsonify({'error': 'Invalid email'}), 400
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT IGNORE INTO newsletter (email) VALUES (%s)', (email,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'ok': True, 'email': email})



@app.post('/api/contact')
def contact_message():
    data=request.get_json(silent=True) or {}
    name=(data.get('name') or '').strip(); email=(data.get('email') or '').strip(); subject=(data.get('subject') or '').strip(); message=(data.get('message') or '').strip()
    if not name or '@' not in email or not message:
        return jsonify({'error':'name, valid email and message are required'}),400
    conn=get_conn(); cur=conn.cursor()
    cur.execute('INSERT INTO contact_messages (name,email,subject,message) VALUES (%s,%s,%s,%s)',(name,email,subject,message))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok':True}),201

def notify_java(order_id, order):
    payload = json.dumps({'order_id': order_id, **order}).encode('utf-8')
    req = Request(JAVA_ORDER_URL, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(req, timeout=2) as response:
            return response.status == 200
    except (URLError, HTTPError, TimeoutError):
        return False


@app.post('/api/orders')
def create_order():
    data = request.get_json(silent=True) or {}
    customer_name = (data.get('customer_name') or '').strip()
    customer_phone = (data.get('customer_phone') or '').strip()
    customer_address = (data.get('customer_address') or '').strip()
    items = data.get('items') or []

    if not customer_name or not customer_phone or not customer_address or not items:
        return jsonify({'error': 'customer_name, customer_phone, customer_address and items are required'}), 400

    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        validated = []
        total = Decimal('0')

        for item in items:
            product_id = int(item.get('id', 0))
            qty = int(item.get('qty', 0))
            if product_id <= 0 or qty <= 0:
                raise ValueError('Invalid cart item')

            cur.execute('SELECT id, name, price, stock FROM products WHERE id=%s FOR UPDATE', (product_id,))
            product = cur.fetchone()
            if not product:
                raise ValueError(f'Product {product_id} not found')
            if product['stock'] < qty:
                raise ValueError(f"Stock insuffisant pour {product['name']}")

            price = Decimal(str(product['price']))
            total += price * qty
            validated.append((product, qty, price))

        cur.execute('''
            INSERT INTO orders (customer_name, customer_phone, customer_address, total, status)
            VALUES (%s,%s,%s,%s,'pending')
        ''', (customer_name, customer_phone, customer_address, total))
        order_id = cur.lastrowid

        for product, qty, price in validated:
            cur.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s,%s,%s,%s)
            ''', (order_id, product['id'], qty, price))
            cur.execute('UPDATE products SET stock = stock - %s WHERE id=%s', (qty, product['id']))

        conn.commit()
    except (Error, ValueError) as exc:
        conn.rollback()
        return jsonify({'error': str(exc)}), 400
    finally:
        cur.close()
        conn.close()

    java_notified = notify_java(order_id, {
        'customer_name': customer_name,
        'customer_phone': customer_phone,
        'customer_address': customer_address,
        'total': float(total),
        'status': 'pending',
    })

    return jsonify({
        'ok': True,
        'order_id': order_id,
        'total': float(total),
        'java_notified': java_notified,
    }), 201


@app.get('/api/orders')
def list_orders():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM orders ORDER BY created_at DESC, id DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for row in rows:
        row['total'] = json_safe(row['total'])
    return jsonify(rows)


PAGE_MAP = {
    '': 'index.html', 'index.html': 'index.html', 'boutique': 'boutique.html', 'boutique.html': 'boutique.html',
    'histoire': 'histoire.html', 'histoire.html': 'histoire.html', 'blog': 'blog.html', 'blog.html': 'blog.html',
    'contact': 'contact.html', 'contact.html': 'contact.html', 'panier': 'panier.html', 'panier.html': 'panier.html',
}

@app.get('/')
@app.get('/<path:page>')
def website(page=''):
    if page.startswith('api/'):
        return jsonify({'error': 'Not Found'}), 404
    if page in PAGE_MAP:
        return send_from_directory(BASE_DIR, PAGE_MAP[page])
    return send_from_directory(BASE_DIR, page)


if __name__ == '__main__':
    init_database()
    app.run(host='127.0.0.1', port=5000, debug=True)
