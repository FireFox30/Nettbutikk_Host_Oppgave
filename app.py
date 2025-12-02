from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "hemmelig_nøkkel"

# Databasetilkobling
def get_db():
    return mysql.connector.connect(host="localhost", user="root", password="", database="nettbutikk")

# Hjemmeside - vis alle produkter
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    db.close()
    return render_template('index.html', products=products)

# Legg produkt til handlekurv (lagret i session)
@app.route('/add/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = {}
    session['cart'][str(id)] = session['cart'].get(str(id), 0) + 1
    session.modified = True
    return redirect(url_for('cart'))

# Vis handlekurv med produkter og totalpris
@app.route('/cart')
def cart():
    cart_data = session.get('cart', {})
    if not cart_data:
        return render_template('cart.html', items=[], total=0)
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # Hent produktdetaljer fra database
    placeholders = ','.join(['%s'] * len(cart_data.keys()))
    query = f"SELECT * FROM products WHERE id IN ({placeholders})"
    cursor.execute(query, list(cart_data.keys()))
    products = cursor.fetchall()
    db.close()
    
    items = [{'product': p, 'qty': cart_data[str(p['id'])]} for p in products]
    total = sum(p['price'] * cart_data[str(p['id'])] for p in products)
    return render_template('cart.html', items=items, total=total)

# Oppdater antall i handlekurv (+ eller -)
@app.route('/update/<int:id>/<action>')
def update(id, action):
    if 'cart' in session and str(id) in session['cart']:
        if action == 'add':
            session['cart'][str(id)] += 1
        elif action == 'sub':
            session['cart'][str(id)] -= 1
            if session['cart'][str(id)] <= 0:
                del session['cart'][str(id)]
        session.modified = True
    return redirect(url_for('cart'))

# Kasse - lagre ordre til database og tøm handlekurv
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        cart_data = session.get('cart', {})
        if not cart_data:
            return redirect(url_for('index'))
        
        # Hent produkter fra database
        db = get_db()
        cursor = db.cursor(dictionary=True)
        placeholders = ','.join(['%s'] * len(cart_data.keys()))
        query = f"SELECT * FROM products WHERE id IN ({placeholders})"
        cursor.execute(query, list(cart_data.keys()))
        products = cursor.fetchall()
        
        total = sum(p['price'] * cart_data[str(p['id'])] for p in products)
        
        # Lagre ordre
        cursor.execute(
            "INSERT INTO orders (customer_name, customer_email, customer_address, total_price, order_date) VALUES (%s, %s, %s, %s, %s)",
            (request.form['name'], request.form['email'], request.form['address'], total, datetime.now())
        )
        order_id = cursor.lastrowid
        
        # Lagre ordrelinjer
        for p in products:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, product_name, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                (order_id, p['id'], p['name'], cart_data[str(p['id'])], p['price'])
            )
        
        db.commit()
        db.close()
        
        session.pop('cart', None)
        return redirect(url_for('confirmation', order_id=order_id))
    
    return render_template('checkout.html')

# Vis ordrebekreftelse med detaljer
@app.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    
    cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
    order_items = cursor.fetchall()
    
    db.close()
    
    if not order:
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', order=order, order_items=order_items)

if __name__ == '__main__':
    app.run(debug=True)