import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib.ticker as mtick
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import os

# --- HELPER FUNCTIONS ---
def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# 1. CONFIGURATION PARAMETERS
print("\n" + "═"*60)
print("   STRATEGIC PORTFOLIO ANALYSIS: MONTHLY METHOD")
print("═"*60 + "\n")

tickers_input = input("» Asset Identifiers (Tickers): ").upper().split()

while True:
    try:
        monthly_mxn = float(input("\n» Monthly investment flow (MXN): "))
        if monthly_mxn >= 1: break
        else: print("❌ ERROR: Capital must be >= 1.")
    except ValueError:
        print("❌ ERROR: Please enter numeric values.")

weights = []
if len(tickers_input) == 1:
    weights = [1.0]
else:
    while True:
        weights = []
        for t in tickers_input:
            try:
                w = float(input(f"   └─ % for {t}: "))
                weights.append(w / 100)
            except ValueError: break
        if len(weights) == len(tickers_input) and round(sum(weights), 2) == 1.0: break
        else: print("❌ ERROR: The sum must be 100%.")

while True:
    start_date = input("\n» Start date (YYYY-MM-DD): ")
    if validate_date(start_date): break
    else: print("❌ ERROR: Invalid format.")

while True:
    end_date = input("» End date (Empty for today): ")
    if not end_date: end_date = datetime.today().strftime('%Y-%m-%d'); break
    if validate_date(end_date) and end_date > start_date: break
    else: print("❌ ERROR: Inconsistent chronology.")

# 2. PROCESSING
print("\n[PROCESSING: Synchronizing monthly data...]")
cetes_ticker = "CETETRC.MX" # Mexican Treasury Bonds ETF
data = yf.download(tickers_input + [cetes_ticker, "MXNUSD=X"], start=start_date, end=end_date, auto_adjust=True, progress=False)['Close']
data = data.ffill().dropna()

if data.empty:
    print("\n❌ ERROR: No data retrieved.")
else:
    monthly_data = data.resample('ME').last()
    exchange_rate = monthly_data["MXNUSD=X"]
    total_capital = monthly_mxn * len(monthly_data)
    res_dca, res_bh = pd.Series(0.0, index=monthly_data.index), pd.Series(0.0, index=monthly_data.index)

    for i, t in enumerate(tickers_input):
        current_price = monthly_data[t]
        monthly_usd = (monthly_mxn * weights[i]) * exchange_rate
        shares = (monthly_usd / current_price).cumsum()
        res_dca = res_dca + ((shares * current_price) / exchange_rate)
        initial_usd = (total_capital * weights[i]) * exchange_rate.iloc[0]
        res_bh = res_bh + (((initial_usd / current_price.iloc[0]) * current_price) / exchange_rate)

    cetes_value = (monthly_mxn / monthly_data[cetes_ticker]).cumsum() * monthly_data[cetes_ticker]
    cash_cushion = pd.Series(monthly_mxn, index=monthly_data.index).cumsum()

    # 3. GRAPHICAL INTERFACE
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=100)

    currency_fmt = mtick.StrMethodFormatter('${x:,.0f}')
    date_fmt = mdates.DateFormatter('%b %Y')

    ax1.plot(res_dca, color='#00E676', linewidth=3, label='DCA Strategy', zorder=3)
    ax1.plot(cetes_value, color='#FFAB40', linestyle='--', alpha=0.8, label='CETES (Treasury Bonds)')
    ax1.fill_between(cash_cushion.index, cash_cushion, color='white', alpha=0.07, label='Base Savings (Cushion)')
    ax1.set_title('MONTHLY EVOLUTION: DCA VS. BASE SAVINGS', fontsize=12, pad=20, fontweight='bold')

    ax2.plot(res_bh, color='#2979FF', linewidth=3, label='Buy & Hold', zorder=3)
    ax2.plot(res_dca, color='#00E676', linewidth=3, label='DCA Strategy', zorder=2)
    ax2.set_title('STRATEGIC COMPARISON: DCA VS. B&H', fontsize=12, pad=20, fontweight='bold')

    for ax in [ax1, ax2]:
        ax.yaxis.set_major_formatter(currency_fmt)
        ax.xaxis.set_major_formatter(date_fmt)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=12))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=9, color='#AAAAAA')
        ax.grid(color='#333333', linestyle=':', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(frameon=False, fontsize=10, loc='upper left')

    plt.tight_layout(pad=4)
    plt.show()

    # 4. ON-SCREEN REPORT (Terminal Adapted)
    r_dca = (res_dca.iloc[-1] / total_capital - 1) * 100
    r_bh = (res_bh.iloc[-1] / total_capital - 1) * 100

    print("\n" + "="*50)
    print(" STRATEGIC PERFORMANCE REPORT")
    print("="*50)
    print(f" Monthly Analysis: {start_date} — {end_date}")
    print("\n [ FINANCIAL SUMMARY ]")
    print(f" Base Savings (Accumulated): ${total_capital:,.2f} MXN")
    print(f" Analyzed Portfolio:         {', '.join(tickers_input)}")
    print("\n [ CAPITAL GAIN OVER NOMINAL SAVINGS ]")
    print(f" CETES Capital Gain:         ${(cetes_value.iloc[-1] - total_capital):,.2f} MXN")
    print(f" DCA Capital Gain:           ${(res_dca.iloc[-1] - total_capital):,.2f} MXN ({r_dca:+.2f}%)")
    print(f" Buy & Hold Capital Gain:    ${(res_bh.iloc[-1] - total_capital):,.2f} MXN ({r_bh:+.2f}%)")
    print("="*50 + "\n")

    # --- 5. EXPORT INTERFACE (Terminal Adapted) ---
    save_pdf = input("Do you want to generate the PDF report? (y/n): ").strip().lower()
    
    if save_pdf == 'y':
        final_name = input("File name (without .pdf): ").strip() or "Investment_Report"
        pdf_path = f"{final_name}.pdf"
        
        print("\n⏳ Processing PDF file...")
        
        with PdfPages(pdf_path) as pdf:
            pdf.savefig(fig, bbox_inches='tight')
            fig_rep = plt.figure(figsize=(11, 8))
            ax_rep = fig_rep.add_axes([0, 0, 1, 1])
            ax_rep.axis('off')
            ax_rep.add_patch(Rectangle((0.02, 0.05), 0.96, 0.9, fill=False, linewidth=2))
            ax_rep.text(0.5, 0.90, "DETAILED PERFORMANCE REPORT", ha='center', fontsize=20, fontweight='bold')
            ax_rep.text(0.5, 0.85, f"Period: {start_date} to {end_date}", ha='center', fontsize=14)
            ax_rep.plot([0.04, 0.96], [0.80, 0.80], color='black', linewidth=2)

            y_pos, gap = 0.72, 0.10
            rows = [
                ("1. Pure Savings (Cushion)", f"${total_capital:,.2f} MXN"),
                ("2. CETES Result", f"${cetes_value.iloc[-1]:,.2f} MXN"),
                ("3. DCA Result (Assets)", f"${res_dca.iloc[-1]:,.2f} MXN"),
                ("4. Buy & Hold Result", f"${res_bh.iloc[-1]:,.2f} MXN"),
            ]
            for c, v in rows:
                ax_rep.text(0.06, y_pos, c, fontsize=15)
                ax_rep.text(0.94, y_pos, v, fontsize=15, ha='right')
                y_pos -= gap

            ax_rep.plot([0.04, 0.96], [y_pos + 0.03, y_pos + 0.03], color='black', linewidth=2)
            diff = res_bh.iloc[-1] - res_dca.iloc[-1]
            ax_rep.text(0.06, y_pos - 0.05, "DIFFERENCE (B&H - DCA)", fontsize=16, fontweight='bold')
            ax_rep.text(0.94, y_pos - 0.05, f"${diff:,.2f} MXN", fontsize=16, fontweight='bold', ha='right')

            pdf.savefig(fig_rep, bbox_inches='tight')
            plt.close(fig_rep)

        print(f"✅ Success! File saved locally as: {pdf_path}")
    else:
        print("ℹ️ PDF report canceled. Session ended.")
