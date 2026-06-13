# Quantitative Portfolio Simulator: DCA vs. Lump Sum 📈

This is my Final Project for Stanford University's **Code in Place**. 

This Python-based Command Line Interface (CLI) tool fetches historical market data using the Yahoo Finance API to run a comparative financial analysis between two popular investment strategies: **Dollar Cost Averaging (DCA)** and **Lump Sum (Buy & Hold)**.

## Features
* **Automated Data Retrieval:** Pulls historical price data directly from Yahoo Finance.
* **Strategy Comparison:** Calculates and compares the capital gains of investing a fixed monthly amount (DCA) versus a single initial investment (Lump Sum/Buy & Hold).
* **Base Savings & Treasury Benchmark:** Includes a baseline comparison against a zero-yield cash cushion and Mexican Treasury Bonds (CETES).
* **Data Visualization:** Generates dark-themed, professional matplotlib charts to visualize portfolio growth over time.
* **PDF Reporting:** Allows the user to export a detailed performance summary into a formatted PDF file.

## Prerequisites
To run this script locally, you will need Python installed along with the following external libraries:

    pip install yfinance pandas matplotlib

## How to Use
Run the script from your terminal:

    python3 Data_Prov.py

### ⚠️ Important Input Rules
When the program prompts you for the information, please note the following:
1. **Valid Tickers:** You must input the exact ticker symbols as they appear on **Yahoo Finance** (e.g., AAPL, MSFT, BTC-USD). If the ticker is incorrect or doesn't exist in their database, the program will not be able to fetch the data.
2. **Space-Separated:** If you are analyzing a multi-asset portfolio, enter the tickers on a single line, separated only by spaces. 
   * *Example:* AAPL MSFT GOOG
3. **Report Generation:** At the end of the simulation, the terminal will ask if you want to generate a PDF report. If you type 'y' (yes), you will be prompted to name the file, and the PDF will be automatically saved in the same directory.
4. You can change the badge and CETES to your country Treasury Certificate (the minimum risk instrument) to change the benchmark according your inflations country.

## Output Example
The script provides a clean terminal summary and generates a visual layout containing:
* A timeline comparing the DCA strategy against pure savings and CETES.
* A direct head-to-head chart of DCA vs. Buy & Hold.
* A downloadable PDF containing the exact monetary differences between the strategies.
