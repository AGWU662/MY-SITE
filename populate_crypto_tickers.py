"""
Populate CryptoTicker model with initial cryptocurrency data
Run with: python manage.py shell < populate_crypto_tickers.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elite_wealth_capital.settings')
django.setup()

from investments.models import CryptoTicker

# Common cryptocurrencies with their CoinGecko IDs
cryptos = [
    {'symbol': 'BTC', 'name': 'Bitcoin', 'coingecko_id': 'bitcoin', 'display_order': 1},
    {'symbol': 'ETH', 'name': 'Ethereum', 'coingecko_id': 'ethereum', 'display_order': 2},
    {'symbol': 'USDT', 'name': 'Tether', 'coingecko_id': 'tether', 'display_order': 3},
    {'symbol': 'BNB', 'name': 'BNB', 'coingecko_id': 'binancecoin', 'display_order': 4},
    {'symbol': 'SOL', 'name': 'Solana', 'coingecko_id': 'solana', 'display_order': 5},
    {'symbol': 'XRP', 'name': 'XRP', 'coingecko_id': 'ripple', 'display_order': 6},
    {'symbol': 'USDC', 'name': 'USD Coin', 'coingecko_id': 'usd-coin', 'display_order': 7},
    {'symbol': 'ADA', 'name': 'Cardano', 'coingecko_id': 'cardano', 'display_order': 8},
    {'symbol': 'DOGE', 'name': 'Dogecoin', 'coingecko_id': 'dogecoin', 'display_order': 9},
    {'symbol': 'TRX', 'name': 'TRON', 'coingecko_id': 'tron', 'display_order': 10},
    {'symbol': 'DOT', 'name': 'Polkadot', 'coingecko_id': 'polkadot', 'display_order': 11},
    {'symbol': 'MATIC', 'name': 'Polygon', 'coingecko_id': 'matic-network', 'display_order': 12},
    {'symbol': 'LTC', 'name': 'Litecoin', 'coingecko_id': 'litecoin', 'display_order': 13},
    {'symbol': 'SHIB', 'name': 'Shiba Inu', 'coingecko_id': 'shiba-inu', 'display_order': 14},
    {'symbol': 'AVAX', 'name': 'Avalanche', 'coingecko_id': 'avalanche-2', 'display_order': 15},
    {'symbol': 'UNI', 'name': 'Uniswap', 'coingecko_id': 'uniswap', 'display_order': 16},
    {'symbol': 'LINK', 'name': 'Chainlink', 'coingecko_id': 'chainlink', 'display_order': 17},
    {'symbol': 'ATOM', 'name': 'Cosmos', 'coingecko_id': 'cosmos', 'display_order': 18},
    {'symbol': 'XLM', 'name': 'Stellar', 'coingecko_id': 'stellar', 'display_order': 19},
    {'symbol': 'XMR', 'name': 'Monero', 'coingecko_id': 'monero', 'display_order': 20},
]

# Create or update tickers
created_count = 0
updated_count = 0

for crypto in cryptos:
    ticker, created = CryptoTicker.objects.update_or_create(
        symbol=crypto['symbol'],
        defaults={
            'name': crypto['name'],
            'coingecko_id': crypto['coingecko_id'],
            'display_order': crypto['display_order'],
            'is_active': True
        }
    )
    if created:
        created_count += 1
        print(f"✓ Created: {ticker}")
    else:
        updated_count += 1
        print(f"↻ Updated: {ticker}")

print(f"\n✅ Done! Created {created_count} new tickers, updated {updated_count} existing tickers.")
print(f"Total active tickers: {CryptoTicker.objects.filter(is_active=True).count()}")
