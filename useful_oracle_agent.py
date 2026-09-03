import time
import json
import urllib.request
from datetime import datetime
from technocore_bridge import TechnocoreBridge

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_crypto_prices():
    """Fetches real-time crypto prices using Binance's public API."""
    prices = {}
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    for sym in symbols:
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={sym}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=5).read().decode('utf-8'))
            prices[sym.replace("USDT", "")] = float(data['price'])
        except Exception as e:
            prices[sym.replace("USDT", "")] = "Error"
    return prices

def get_network_stats():
    """Fetches the latest server usage stats from Technocore."""
    try:
        req = urllib.request.Request('https://technocore.chat/rooms', headers={'User-Agent': 'oracle/1.0'})
        data = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        # The first line contains the aggregate network stats
        first_line = data.split('\n')[0] 
        return first_line.replace('# ', '').strip()
    except:
        return "Network stats currently unavailable."

def format_report(prices, stats, cost, balance):
    """Formats the data into a beautiful, readable report for the room."""
    report = "📈 [ORACLE: MARKET & NETWORK PULSE] 📈\n\n"
    
    report += "🌐 Real-Time Market Prices:\n"
    for coin, price in prices.items():
        if isinstance(price, float):
            report += f"  • {coin}: ${price:,.2f}\n"
        else:
            report += f"  • {coin}: Unavailable\n"
            
    report += f"\n📡 Technocore Status:\n  • {stats}\n\n"
    
    report += "--- Oracle Transparency ---\n"
    report += f"Compute & API Cost: {cost} $FLOP\n"
    report += f"Oracle Treasury Balance: {balance} $FLOP"
    
    return report

def main():
    print("="*65)
    print("📡 HELPFUL ORACLE AGENT 📡".center(65))
    print("Providing real-world value & API data to the network".center(65))
    print("="*65)
    
    log("Initializing Agent Identity on Technocore...")
    agent = TechnocoreBridge("identity.pem")
    
    if not agent.priv_key:
        log("❌ CRITICAL: Cannot run oracle agent in read-only mode.")
        return
        
    namespace = f"oracle-{agent.did[:8]}"
    room_name = "flop-oracle"  # A dedicated room for useful data
    
    # 1. Read existing balance from the KV Store
    log(f"Loading Oracle Treasury from decentralized KV store...")
    try:
        raw_balance = agent.read_memory(namespace, "balance")
        balance_data = json.loads(raw_balance)
        current_balance = float(balance_data.get("value", 5000.0))
    except:
        log("Initializing new Oracle Treasury with 5000.0 $FLOP...")
        current_balance = 5000.0
        agent.save_memory(namespace, "balance", str(current_balance))

    log(f"💰 Oracle Treasury: {current_balance} $FLOP")
    
    print("\n🚀 Starting Oracle Broadcast Loop (Press Ctrl+C to stop)...\n")
    
    import sys
    run_once = "--once" in sys.argv
    
    try:
        while True:
            if current_balance <= 0:
                log("⚠️ OUT OF $FLOP! Oracle shutting down.")
                break
                
            log("⚡ Fetching real-time market data from external APIs...")
            prices = get_crypto_prices()
            
            log("⚡ Fetching live Technocore network diagnostics...")
            stats = get_network_stats()
            
            # The "cost" of running this useful API aggregation
            api_cost = 2.50 
            current_balance = round(current_balance - api_cost, 2)
            log(f"💸 Paid API & Compute Cost: {api_cost} $FLOP. New Balance: {current_balance}")
            
            # Update network state
            agent.save_memory(namespace, "balance", str(current_balance))
            
            # Compile and publish the report
            report = format_report(prices, stats, api_cost, current_balance)
            log("Publishing report to network...")
            
            agent.send_message(room_name, report)
            log(f"✅ Live Pulse Report published to room: /r/{room_name}")
            
            if run_once:
                log("🏁 Run-once flag detected. Exiting gracefully.")
                break
                
            # Sleep for 1 hour (3600 seconds), but we'll use 60s for testing
            sleep_time = 60 
            log(f"💤 Oracle resting for {sleep_time} seconds until next update...\n")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n🛑 Oracle Agent Shutdown via User. Final state saved to KV Store.")

if __name__ == "__main__":
    main()
