import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Tytuł strony
st.set_page_config(page_title="Strategia GEM", page_icon="📈")
st.title("📈 Strategia GEM (12-1)")

# 1. Konfiguracja Tickerów (Wszystkie z Londynu dla USD)
etf_map = {
    'EIMI (Emerging Mkt)': 'EIMI.L',
    'IWDA (World)': 'IWDA.L',
    'CNDX (Nasdaq 100)': 'CNDX.L',
    'IB01 (Bonds 0-1y)': 'IB01.L',
    'CBU0 (Bonds 7-10y)': 'CBU0.L'
}

# 2. Obliczanie Dat
today = date.today()
first_day_current_month = today.replace(day=1)
first_day_last_month = first_day_current_month - relativedelta(months=1)
end_date = first_day_last_month - timedelta(days=1)
start_date = end_date.replace(year=end_date.year - 1) + timedelta(days=1)

st.write(f"📅 **Data analizy:** {today}")
st.info(f"Badany przedział (Momentum 12-1): **{start_date}** do **{end_date}**")

# Przycisk uruchamiający
if st.button("Oblicz wyniki 🔄"):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_tickers = len(etf_map)
    
    for i, (name, ticker) in enumerate(etf_map.items()):
        status_text.text(f"Pobieranie danych dla: {name}...")
        try:
            t = yf.Ticker(ticker)
            # Pobieranie historii
            df = t.history(start=start_date, end=end_date + timedelta(days=5), auto_adjust=False)
            
            if not df.empty:
                df.index = pd.to_datetime(df.index).date
                df_filtered = df[df.index <= end_date]
                
                if not df_filtered.empty:
                    start_price = float(df_filtered.iloc[0]['Close'])
                    end_price = float(df_filtered.iloc[-1]['Close'])
                    growth = ((end_price - start_price) / start_price) * 100
                    
                    results.append({
                        'ETF': name,
                        'Ticker': ticker,
                        'Cena Start ($)': round(start_price, 2),
                        'Cena Koniec ($)': round(end_price, 2),
                        'Wzrost (%)': round(growth, 2)
                    })
        except Exception as e:
            st.error(f"Błąd dla {name}: {e}")
        
        # Aktualizacja paska postępu
        progress_bar.progress((i + 1) / total_tickers)

    status_text.empty()
    progress_bar.empty()

    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values(by='Wzrost (%)', ascending=False).reset_index(drop=True)

        # Wyświetlenie tabeli
        st.subheader("Wyniki")
        st.dataframe(df_results.style.format({
            "Cena Start ($)": "{:.2f}",
            "Cena Koniec ($)": "{:.2f}",
            "Wzrost (%)": "{:.2f}%"
        }))

        # Wyłonienie zwycięzcy
        winner = df_results.iloc[0]
        st.divider()
        st.subheader("🏆 Decyzja Strategiczna")
        
        col1, col2 = st.columns(2)
        col1.metric("Lider", winner['ETF'])
        col2.metric("Wynik Lidera", f"{winner['Wzrost (%)']}%")

        # Logika decyzyjna GEM
        equity_keywords = ['EIMI', 'IWDA', 'CNDX']
        is_equity = any(x in winner['ETF'] for x in equity_keywords)

        if is_equity and winner['Wzrost (%)'] > 0:
            st.success(f"✅ **SYGNAŁ:** Kupuj/Trzymaj **{winner['ETF']}** (Akcje)")
        else:
            bond_winner = df_results[df_results['Ticker'].isin(['IB01.L', 'CBU0.L'])].iloc[0]
            st.warning(f"🛡️ **SYGNAŁ:** Ucieczka do bezpiecznej przystani -> **{bond_winner['ETF']}** (Obligacje)")
    else:
        st.error("Nie udało się pobrać danych.")