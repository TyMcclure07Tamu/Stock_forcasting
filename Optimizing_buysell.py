import os
import pandas as pd
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import seaborn as sns


# Read the CSV file once globally
current_directory = os.getcwd()
input_file_path = os.path.join(current_directory, 'FinalDatabase.csv')
data = pd.read_csv(input_file_path)
data['date'] = pd.to_datetime(data['date'], errors='coerce', format='%d%b%Y')
data['rdq'] = pd.to_datetime(data['rdq'], errors='coerce', format='%d%b%Y')
data.dropna(subset=['date', 'price'], inplace=True)

def calculate_adjusted_daily_returns(D0, D1):
    results = []

    for firm_id in data['firm_id'].unique():
        firm_data = data[data['firm_id'] == firm_id].sort_values('date')

        for rdq in firm_data['rdq'].unique():
            rdq_date = pd.to_datetime(rdq)
            start_date = rdq_date - BDay(D0)
            end_date = rdq_date + BDay(D1)

            start_data = firm_data[(firm_data['date'] <= start_date) & (~pd.isna(firm_data['price']))]
            end_data = firm_data[(firm_data['date'] >= end_date) & (~pd.isna(firm_data['price']))]

            if not start_data.empty and not end_data.empty:
                adjusted_start_date = start_data.iloc[-1]['date']
                adjusted_end_date = end_data.iloc[0]['date']

                price_start = start_data.iloc[-1]['price']
                price_end = end_data.iloc[0]['price']

                days = (adjusted_end_date - adjusted_start_date).days
                if days > 0:
                    stock_return = ((price_end - price_start) / price_start) / days
                    results.append({
                        'firm_id': firm_id,
                        'rdq': rdq,
                        'daily_return': stock_return,
                        'adjusted_start_date': adjusted_start_date.strftime('%Y-%m-%d'),
                        'adjusted_end_date': adjusted_end_date.strftime('%Y-%m-%d'),
                        'days': days
                    })

    return pd.DataFrame(results)

def optim_buy_sell(output_file_path):
    optim_results = []

    for D0 in range(11):  # Days before: 0 to 10
        for D1 in range(5, 16):  # Days after: 5 to 15
            results_df = calculate_adjusted_daily_returns(D0, D1)
            if not results_df.empty:
                avg_daily_return = results_df['daily_return'].mean()
                optim_results.append((D0, D1, avg_daily_return))

    optim_df = pd.DataFrame(optim_results, columns=['Days Before', 'Days After', 'Average Return'])
    optim_df.to_csv(output_file_path, index=False)
    print("Optimization results:")
    print(optim_df)

output_file_path = os.path.join(current_directory, 'OptimizedBuySell.csv')
optim_buy_sell(output_file_path)

df = pd.read_csv('OptimizedBuySell.csv')

df['Average Return'] = df['Average Return'].round(7)

df['Average Return'] = (df['Average Return']*100).round(4)

df = df.sort_values(by = 'Average Return', ascending = False)

# Save the modified DataFrame back to a CSV file
output_file_path = 'Final_OptimizedBuySell.csv'
df.to_csv(output_file_path, index=False)

print(f"File saved as {output_file_path}")


def plot_results(optim_results):
    df = pd.DataFrame(optim_results, columns=['Days Before', 'Days After', 'Average Return'])
    
    # Correcting the pivot method usage
    pivot_table = df.pivot(index='Days Before', columns='Days After', values='Average Return')
    
    # Create a heatmap
    plt.figure(figsize=(10, 8))
    plt.title('Optimization Results Heatmap')
    sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap='coolwarm')
    
    # Save the figure
    plt.savefig(os.path.join(current_directory, 'Optimization_Heatmap.png'))
    plt.close()

plot_results(df)