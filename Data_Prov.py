import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib.ticker as mtick
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import os

# --- FUNCIONES DE APOYO ---
def validar_fecha(texto_input):
    try:
        datetime.strptime(texto_input, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# 1. PARÁMETROS DE CONFIGURACIÓN
print("\n" + "═"*60)
print("   ANÁLISIS ESTRATÉGICO DE CARTERA: MÉTODO MENSUALIZADO")
print("═"*60 + "\n")

tickers_input = input("» Identificadores de Activos (Tickers): ").upper().split()

while True:
    try:
        m_mxn = float(input("\n» Flujo de inversión mensual (MXN): "))
        if m_mxn >= 1: break
        else: print("❌ ERROR: El capital debe ser >= 1.")
    except ValueError:
        print("❌ ERROR: Ingrese valores numéricos.")

pesos = []
if len(tickers_input) == 1:
    pesos = [1.0]
else:
    while True:
        pesos = []
        for t in tickers_input:
            try:
                p = float(input(f"   └─ % para {t}: "))
                pesos.append(p / 100)
            except ValueError: break
        if len(pesos) == len(tickers_input) and round(sum(pesos), 2) == 1.0: break
        else: print("❌ ERROR: La suma debe ser 100%.")

while True:
    f_ini = input("\n» Fecha de inicio (AAAA-MM-DD): ")
    if validar_fecha(f_ini): break
    else: print("❌ ERROR: Formato inválido.")

while True:
    f_fin = input("» Fecha de fin (Vacío para hoy): ")
    if not f_fin: f_fin = datetime.today().strftime('%Y-%m-%d'); break
    if validar_fecha(f_fin) and f_fin > f_ini: break
    else: print("❌ ERROR: Cronología inconsistente.")

# 2. PROCESAMIENTO
print("\n[PROCESANDO: Sincronizando datos mensuales...]")
t_cetes = "CETETRC.MX"
data = yf.download(tickers_input + [t_cetes, "MXNUSD=X"], start=f_ini, end=f_fin, auto_adjust=True, progress=False)['Close']
data = data.ffill().dropna()

if data.empty:
    print("\n❌ ERROR: No se obtuvieron datos.")
else:
    ld = data.resample('ME').last()
    tc = ld["MXNUSD=X"]
    cap_total = m_mxn * len(ld)
    res_dca, res_bh = pd.Series(0.0, index=ld.index), pd.Series(0.0, index=ld.index)

    for i, t in enumerate(tickers_input):
        p_act = ld[t]
        m_usd = (m_mxn * pesos[i]) * tc
        tit = (m_usd / p_act).cumsum()
        res_dca = res_dca + ((tit * p_act) / tc)
        m_ini_usd = (cap_total * pesos[i]) * tc.iloc[0]
        res_bh = res_bh + (((m_ini_usd / p_act.iloc[0]) * p_act) / tc)

    v_cetes = (m_mxn / ld[t_cetes]).cumsum() * ld[t_cetes]
    colchon = pd.Series(m_mxn, index=ld.index).cumsum()

    # 3. INTERFAZ GRÁFICA
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=100)

    fmt_moneda = mtick.StrMethodFormatter('${x:,.0f}')
    fmt_fecha = mdates.DateFormatter('%b %Y')

    ax1.plot(res_dca, color='#00E676', linewidth=3, label='Estrategia DCA', zorder=3)
    ax1.plot(v_cetes, color='#FFAB40', linestyle='--', alpha=0.8, label='CETES')
    ax1.fill_between(colchon.index, colchon, color='white', alpha=0.07, label='Ahorro Base (Colchón)')
    ax1.set_title('EVOLUCIÓN MENSUAL: DCA VS. AHORRO BASE', fontsize=12, pad=20, fontweight='bold')

    ax2.plot(res_bh, color='#2979FF', linewidth=3, label='Buy & Hold', zorder=3)
    ax2.plot(res_dca, color='#00E676', linewidth=3, label='DCA Strategy', zorder=2)
    ax2.set_title('COMPARATIVA ESTRATÉGICA: DCA VS. B&H', fontsize=12, pad=20, fontweight='bold')

    for ax in [ax1, ax2]:
        ax.yaxis.set_major_formatter(fmt_moneda)
        ax.xaxis.set_major_formatter(fmt_fecha)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=12))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=9, color='#AAAAAA')
        ax.grid(color='#333333', linestyle=':', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(frameon=False, fontsize=10, loc='upper left')

    plt.tight_layout(pad=4)
    plt.show()

    # 4. REPORTE EN PANTALLA (Adaptado para Terminal)
    r_dca = (res_dca.iloc[-1]/cap_total-1)*100
    r_bh = (res_bh.iloc[-1]/cap_total-1)*100

    print("\n" + "="*50)
    print(" REPORTE ESTRATÉGICO DE RENDIMIENTO")
    print("="*50)
    print(f" Análisis Mensualizado: {f_ini} — {f_fin}")
    print("\n [ RESUMEN FINANCIERO ]")
    print(f" Ahorro Base (Acumulado): ${cap_total:,.2f} MXN")
    print(f" Cartera Analizada:       {', '.join(tickers_input)}")
    print("\n [ PLUSVALÍA SOBRE EL AHORRO NOMINAL ]")
    print(f" Plusvalía CETES:         ${(v_cetes.iloc[-1] - cap_total):,.2f} MXN")
    print(f" Plusvalía DCA:           ${(res_dca.iloc[-1] - cap_total):,.2f} MXN ({r_dca:+.2f}%)")
    print(f" Plusvalía Buy & Hold:    ${(res_bh.iloc[-1] - cap_total):,.2f} MXN ({r_bh:+.2f}%)")
    print("="*50 + "\n")

    # --- 5. INTERFAZ DE EXPORTACIÓN (Adaptada para Terminal) ---
    guardar = input("¿Deseas generar el reporte en PDF? (s/n): ").strip().lower()
    
    if guardar == 's':
        nombre_final = input("Nombre del archivo (sin .pdf): ").strip() or "Reporte_Inversion"
        ruta_pdf = f"{nombre_final}.pdf"
        
        print("\n⏳ Procesando archivo PDF...")
        
        with PdfPages(ruta_pdf) as pdf:
            pdf.savefig(fig, bbox_inches='tight')
            fig_rep = plt.figure(figsize=(11, 8))
            ax_rep = fig_rep.add_axes([0, 0, 1, 1])
            ax_rep.axis('off')
            ax_rep.add_patch(Rectangle((0.02, 0.05), 0.96, 0.9, fill=False, linewidth=2))
            ax_rep.text(0.5, 0.90, "INFORME DETALLADO DE RENDIMIENTOS", ha='center', fontsize=20, fontweight='bold')
            ax_rep.text(0.5, 0.85, f"Periodo: {f_ini} al {f_fin}", ha='center', fontsize=14)
            ax_rep.plot([0.04, 0.96], [0.80, 0.80], color='black', linewidth=2)

            y_pos, gap = 0.72, 0.10
            filas = [
                ("1. Ahorro Puro (Colchón)", f"${cap_total:,.2f} MXN"),
                ("2. Resultado CETES", f"${v_cetes.iloc[-1]:,.2f} MXN"),
                ("3. Resultado DCA (Activos)", f"${res_dca.iloc[-1]:,.2f} MXN"),
                ("4. Resultado Buy & Hold", f"${res_bh.iloc[-1]:,.2f} MXN"),
            ]
            for c, v in filas:
                ax_rep.text(0.06, y_pos, c, fontsize=15)
                ax_rep.text(0.94, y_pos, v, fontsize=15, ha='right')
                y_pos -= gap

            ax_rep.plot([0.04, 0.96], [y_pos + 0.03, y_pos + 0.03], color='black', linewidth=2)
            dif = res_bh.iloc[-1] - res_dca.iloc[-1]
            ax_rep.text(0.06, y_pos - 0.05, "DIFERENCIA (B&H - DCA)", fontsize=16, fontweight='bold')
            ax_rep.text(0.94, y_pos - 0.05, f"${dif:,.2f} MXN", fontsize=16, fontweight='bold', ha='right')

            pdf.savefig(fig_rep, bbox_inches='tight')
            plt.close(fig_rep)

        print(f"✅ ¡Éxito! Archivo guardado localmente como: {ruta_pdf}")
    else:
        print("ℹ️ Reporte PDF cancelado. Sesión finalizada.")