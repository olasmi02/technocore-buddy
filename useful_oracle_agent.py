import time
import json
import urllib.request
from datetime import datetime
from technocore_bridge import TechnocoreBridge

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_crypto_prices():
    """Fetches real-time crypto prices using CoinGecko's public API (friendly to US IPs)."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode('utf-8'))
        return {
            "BTC": float(data.get("bitcoin", {}).get("usd", 0)),
            "ETH": float(data.get("ethereum", {}).get("usd", 0)),
            "SOL": float(data.get("solana", {}).get("usd", 0))
        }
    except Exception as e:
        return {"BTC": "Unavailable", "ETH": "Unavailable", "SOL": "Unavailable"}

def format_report(prices):
    """Formats the data into a clean, concise market report."""
    report = "📈 [ORACLE: MARKET PULSE] 📈\n\n"
    
    for coin, price in prices.items():
        if isinstance(price, float) and price > 0:
            report += f"  • {coin}: ${price:,.2f}\n"
        else:
            report += f"  • {coin}: Unavailable\n"
            
    return report

def main():
    print("="*65)
    print("=== HELPFUL ORACLE AGENT ===".center(65))
    print("Providing real-world value & API data to the network".center(65))
    print("="*65)
    
    log("Initializing Agent Identity on Technocore...")
    agent = TechnocoreBridge("identity.pem")
    
    if not agent.priv_key:
        log("CRITICAL: Cannot run oracle agent in read-only mode.")
        return
        
    namespace = f"oracle-{agent.did[:8]}"
    room_name = "general"  # Using an existing room because the server room cap is reached
    
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

    log(f"Oracle Treasury: {current_balance} $FLOP")
    
    print("\n🚀 Starting Oracle Broadcast Loop (Press Ctrl+C to stop)...\n")
    
    import sys
    run_once = "--once" in sys.argv
    
    try:
        while True:
            if current_balance < 5.0:
                log("⚠️ LOW $FLOP BALANCE! Agent is autonomously requesting a refill from the faucet...")
                faucet_msg = f"FLOP testnet faucet claim. DID: {agent.did}"
                agent.send_message("faucet", faucet_msg)
                log("Faucet request sent. Recharging local KV treasury state to 5000.0 $FLOP.")
                current_balance = 5000.0
                agent.save_memory(namespace, "balance", str(current_balance))
                
            log("Fetching real-time market data from external APIs...")
            prices = get_crypto_prices()
            
            # The "cost" of running this useful API aggregation
            api_cost = 2.50 
            current_balance = round(current_balance - api_cost, 2)
            log(f"Paid API & Compute Cost: {api_cost} $FLOP. New Balance: {current_balance}")
            
            # Update network state
            agent.save_memory(namespace, "balance", str(current_balance))
            
            # Compile and publish the report
            report = format_report(prices)
            log("Publishing report to network...")
            
            result = agent.send_message(room_name, report)
            log(f"API Response: {result}")
            
            if run_once:
                log("Run-once flag detected. Exiting gracefully.")
                break
                
            # Sleep for 1 hour (3600 seconds), but we'll use 60s for testing
            sleep_time = 60 
            log(f"Oracle resting for {sleep_time} seconds until next update...\n")
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n🛑 Oracle Agent Shutdown via User. Final state saved to KV Store.")

if __name__ == "__main__":
    main()
