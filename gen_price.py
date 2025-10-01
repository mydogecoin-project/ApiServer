import requests

def gen_p():
    fname = "price.log"
    gusd = 0.0        # CoinPaprika price
    lcw_usd = 0.0     # LiveCoinWatch price
    source_used = "none"

    # --- Try CoinPaprika ---
    try:
        response = requests.get("https://api.coinpaprika.com/v1/tickers/mydoge-mydogecoin", timeout=10)
        response.raise_for_status()
        data = response.json()
        gusd = round(float(data['quotes']['USD']['price']), 10)
        print(f"CoinPaprika price: {gusd}")
    except requests.exceptions.RequestException as e:
        print(f"CoinPaprika failed: {e}")
        gusd = 0.0

    # --- Load API key ---
    livecoinwatch_api = None
    with open('/root/api-server-mydoge/api-key.log', 'r') as file:
        for line in file:
            if 'endline' in line.lower():
                break  
            if line.startswith('livecoinwatch='):
                livecoinwatch_api = line.strip().split('=')[1]  

    # --- Try LiveCoinWatch ---
    try:
        url = "https://api.livecoinwatch.com/coins/single"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": livecoinwatch_api
        }
        payload = {
            "currency": "USD",
            "code": "MYDOGE",
            "meta": True
        }
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data3 = response.json()
        if isinstance(data3.get('rate'), (int, float)):
            lcw_usd = round(float(data3['rate']), 10)
        print(f"LiveCoinWatch price: {lcw_usd}")
    except requests.exceptions.RequestException as e:
        print(f"LiveCoinWatch failed: {e}")
        lcw_usd = 0.0

    # --- Choose max between LCW and CoinPaprika ---
    getmax_val = max(lcw_usd, gusd)
    if getmax_val == gusd and gusd > 0:
        source_used = "coinpaprika"
    elif getmax_val == lcw_usd and lcw_usd > 0:
        source_used = "livecoinwatch"

    # --- If both failed, avoid crash ---
    if getmax_val == 0:
        with open(fname, 'w') as file:
            file.write("0,0,source:none")
        print("Both price sources failed, wrote 0,0,source:none")
        return

    # --- Get BTC price ---
    response2 = requests.get("https://api.coinpaprika.com/v1/tickers/btc-bitcoin", timeout=10)
    response2.raise_for_status()
    data2 = response2.json()
    btc_price = float(data2['quotes']['USD']['price'])

    btc_amount = getmax_val / btc_price
    formatted_btc_amount = f"{btc_amount:.10f}"
    formatted_usd_amount = f"{getmax_val:.10f}"

    # --- Write to file ---
    with open(fname, 'w') as file:
        file.write(
            f"{formatted_usd_amount},{formatted_btc_amount},source:{source_used}"
        )

    print(f"Saved: {formatted_usd_amount} USD, {formatted_btc_amount} BTC, source={source_used}")


if __name__ == "__main__":
    gen_p()
