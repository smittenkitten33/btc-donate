import os
import time
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# REPLACE THIS WITH YOUR BLUEWALLET ADDRESS
WALLET_ADDRESS = "YOUR_BLUEWALLET_ADDRESS"

# CONFIGURATION
GROWTH_RATE_YEARLY = 0.15  # 15% annual growth (adjust to your liking)
BTC_API_URL = "https://blockchain.info/ticker"
DB_FILE = "transactions.json"

# Initialize simple in-memory DB (for demo purposes)
# In a real production app, use SQLite or Postgres
transactions = []

def get_btc_price():
    """Fetches current BTC price in USD from Blockchain.info"""
    try:
        response = requests.get(BTC_API_URL)
        data = response.json()
        return data['USD']['last']  # Returns last traded price
    except Exception as e:
        print(f"Error fetching price: {e}")
        return 60000  # Fallback price if API fails

def calculate_projection(initial_btc, days_passed):
    """Calculates hypothetical growth over time"""
    price = get_btc_price()
    # Compound interest formula: A = P * (1 + r)^t
    # r = daily rate, t = days
    daily_rate = GROWTH_RATE_YEARLY / 365
    projected_btc = initial_btc * ((1 + daily_rate) ** days_passed)
    projected_usd = projected_btc * price
    return {
        "btc": round(projected_btc, 8),
        "usd": round(projected_usd, 2),
        "current_btc": initial_btc,
        "current_usd": round(initial_btc * price, 2)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    """Returns the current status of the wallet and latest transaction"""
    # Fetch recent transactions from Blockchain.info API
    try:
        url = f"https://blockchain.info/rawaddr/{WALLET_ADDRESS}?limit=1"
        response = requests.get(url)
        txs = response.json()
        
        if txs:
            latest = txs[0]
            amount_btc = latest['value'] / 1e8
            timestamp = latest['time']
            
            # Check if we already logged this transaction
            if not any(t['tx_hash'] == latest['hash'] for t in transactions):
                new_tx = {
                    'tx_hash': latest['hash'],
                    'amount_btc': amount_btc,
                    'timestamp': timestamp,
                    'status': 'confirmed'
                }
                transactions.append(new_tx)
            
            # Calculate projection from the *first* transaction to now
            if transactions:
                first_tx = transactions[0]
                days_passed = (time.time() - first_tx['timestamp']) / 86400
                projection = calculate_projection(first_tx['amount_btc'], days_passed)
                
                return jsonify({
                    'status': 'success',
                    'total_btc': sum(t['amount_btc'] for t in transactions),
                    'projected': projection,
                    'latest_tx': transactions[-1]
                })
            
        return jsonify({'status': 'waiting', 'message': 'Waiting for first donation...'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/chart-data', methods=['GET'])
def chart_data():
    """Returns data points for the graph"""
    if not transactions:
        return jsonify([])
    
    first_tx = transactions[0]
    data_points = []
    
    # Generate data points for the last 30 days
    days = 30
    for i in range(days):
        days_passed = i
        proj = calculate_projection(first_tx['amount_btc'], days_passed)
        data_points.append({
            'day': days - i,
            'btc': proj['btc'],
            'usd': proj['usd']
        })
    
    return jsonify(data_points)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
