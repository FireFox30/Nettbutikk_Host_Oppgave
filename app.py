from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("DB_FLASKKEY")


# Returnerer en ny tilkobling hver gang den kalles for å unngå threading-problemer
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="nettbutikk"
    )

# HJEMMESIDE - Viser alle produkter fra databasen
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    db.close()
    return render_template('index.html', products=products)

@app.route('/test')
def test():
    return "Test successful!"


# Legger til et produkt i handlekurven (lagret i Flask session)
@app.route('/add/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = {}
    # Øker antallet av produktet med 1, get() returnerer 0 hvis produktet ikke finnes, ellers eksisterende antall
    session['cart'][str(id)] = session['cart'].get(str(id), 0) + 1
    session.modified = True
    return redirect(url_for('cart'))


# Viser alle produkter i handlekurven med totalpris
@app.route('/cart')
def cart():
    cart_data = session.get('cart', {})
    
    if not cart_data:
        return render_template('cart.html', items=[], total=0)
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Bygger SQL-query med placeholders (%s) for hvert produkt-ID
    placeholders = ','.join(['%s'] * len(cart_data.keys()))
    query = f"SELECT * FROM products WHERE id IN ({placeholders})"
    
    cursor.execute(query, list(cart_data.keys()))
    products = cursor.fetchall()
    db.close()
    

    # Kombinerer produktinfo fra database med antall fra session
    items = [{'product': p, 'qty': cart_data[str(p['id'])]} for p in products]
    
    # Beregner totalpris: pris * antall for hvert produkt
    total = sum(p['price'] * cart_data[str(p['id'])] for p in products)
    
    return render_template('cart.html', items=items, total=total)



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


# Viser checkout-skjema og behandler ordregjennomføring
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        cart_data = session.get('cart', {})

        if not cart_data:
            return redirect(url_for('index'))
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Henter produktdetaljer fra database for alle produkter i handlekurven
        placeholders = ','.join(['%s'] * len(cart_data.keys()))
        query = f"SELECT * FROM products WHERE id IN ({placeholders})"
        cursor.execute(query, list(cart_data.keys()))
        products = cursor.fetchall()

        total = sum(p['price'] * cart_data[str(p['id'])] for p in products)
        
        cursor.execute(
            "INSERT INTO orders (customer_name, customer_email, customer_address, total_price, order_date) VALUES (%s, %s, %s, %s, %s)",
            (
                request.form['name'],      
                request.form['email'],     
                request.form['address'],   
                total,                     
                datetime.now()
            )
        )
        order_id = cursor.lastrowid
        
        # Lagrer hver ordrelinje (hvert produkt i ordren) i order_items-tabellen
        for p in products:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, product_name, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                (
                    order_id,                      
                    p['id'],                       
                    p['name'],                     
                    cart_data[str(p['id'])],       
                    p['price']
                )
            )
        db.commit()
        db.close()
        session.pop('cart', None)
        
        return redirect(url_for('confirmation', order_id=order_id))
    return render_template('checkout.html')


# Viser ordredetaljer etter vellykket kjøp
@app.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Henter ordren fra orders-tabellen
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