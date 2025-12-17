from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import json


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("DB_FLASKKEY")

# AI API Configuration
AI_API_URL = os.getenv("AI_API_URL", "http://10.2.3.39:8000/support")


# Returnerer en ny tilkobling hver gang den kalles for å unngå threading-problemer
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="nettbutikk"
    )


# AI Query Function
def query_ai(prompt):
    """Query the AI hosted on Raspberry Pi"""
    try:
        print(f"Sending request to: {AI_API_URL}")
        print(f"Prompt: {prompt}")
        
        response = requests.post(
            AI_API_URL,
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt},
            timeout=60  # Increased timeout since your response took 57 seconds
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        response.raise_for_status()
        data = response.json()
        
        # Your API returns 'response' key based on the PowerShell output
        if isinstance(data, dict) and 'response' in data:
            return data['response'].strip()
        elif isinstance(data, dict):
            # Fallback to other common keys
            return (data.get('answer') or 
                   data.get('message') or 
                   data.get('text') or
                   str(data))
        else:
            return str(data)
            
    except requests.exceptions.Timeout:
        print("AI API Timeout - response took too long")
        return "Beklager, AI-en bruker for lang tid på å svare. Prøv igjen."
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return "Beklager, kan ikke koble til AI-serveren. Sjekk at Raspberry Pi er tilgjengelig."
    except requests.exceptions.RequestException as e:
        print(f"AI API Error: {e}")
        print(f"Error type: {type(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error response: {e.response.text}")
        return "Beklager, AI-tjenesten er ikke tilgjengelig akkurat nå."


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


# AI Chat Endpoint
@app.route('/chat', methods=['POST'])
def chat():
    """Handle AI chat requests"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'response': 'Vennligst skriv en melding.'}), 400
    
    # Get products context for better AI responses
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, description, price FROM products")
    products = cursor.fetchall()
    db.close()
    
    # Build context-aware prompt
    product_list = "\n".join([f"- {p['name']}: {p['description']} ({p['price']} kr)" for p in products[:5]])
    
    prompt = f"""Du er en hjelpsom kundeserviceassistent for NerdParts.no, en nettbutikk som selger elektronikkdeler.

Våre produkter inkluderer:
{product_list}

Kunde spør: {user_message}

Svar kort og hjelpsomt på norsk. Hvis kunden spør om produkter vi ikke har, vær ærlig om det."""
    
    ai_response = query_ai(prompt)
    
    return jsonify({'response': ai_response})


# Legger til et produkt i handlekurven (lagret i Flask session)
@app.route('/add/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = {}
    session['cart'][str(id)] = session['cart'].get(str(id), 0) + 1
    session.modified = True
    return redirect(url_for('cart'))


# Viser alle produkter i handlekurven med totalpris
@app.route('/cart')
def cart():
    cart_data = session.get('cart', {})
    
    if not cart_data:
        return render_template('cart.html', items=[], total=0)
    
    # Validate all keys are valid integers (SQL injection protection)
    try:
        product_ids = [int(k) for k in cart_data.keys()]
    except ValueError:
        session.pop('cart', None)
        return redirect(url_for('index'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    placeholders = ','.join(['%s'] * len(product_ids))
    query = f"SELECT * FROM products WHERE id IN ({placeholders})"
    
    cursor.execute(query, product_ids)
    products = cursor.fetchall()
    db.close()
    
    items = [{'product': p, 'qty': cart_data[str(p['id'])]} for p in products]
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
        
        # Validate all keys are valid integers (SQL injection protection)
        try:
            product_ids = [int(k) for k in cart_data.keys()]
        except ValueError:
            session.pop('cart', None)
            return redirect(url_for('index'))
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        placeholders = ','.join(['%s'] * len(product_ids))
        query = f"SELECT * FROM products WHERE id IN ({placeholders})"
        cursor.execute(query, product_ids)
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