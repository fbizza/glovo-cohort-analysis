
import pandas as pd
from tqdm import tqdm
import pickle

import numpy as np
from matplotlib import pyplot as plt

with open('../data/orders.pkl', 'rb') as file:
    loaded_orders = pickle.load(file)

with open('../data/recurrent_customers.pkl', 'rb') as file:
    loaded_recurrent_customers = pickle.load(file)

print(loaded_orders)
print(loaded_recurrent_customers)


def filter_and_count_rc_orders(customers_dict, orders_dict, store_names, verticals):
    results = {}
    for time_span in customers_dict:
        if time_span in orders_dict:
            customers_df = customers_dict[time_span]
            orders_df = orders_dict[time_span]
            # n_recurrent_customers = orders_df.shape[0]
            n_orders_by_recurrent_customers = int(orders_df['customer_id'].isin(customers_df['customer_id']).sum())
            results[time_span] = {}
            results[time_span]['total'] = n_orders_by_recurrent_customers
            results[time_span]['rest'] = n_orders_by_recurrent_customers ## Not correct if vertical and store name overlap
            for store in store_names:
                store_orders_df = orders_df[orders_df['store_name'] == store]
                n_store_orders_by_recurrent_customers = int(store_orders_df['customer_id'].isin(customers_df['customer_id']).sum())
                results[time_span][store] = n_store_orders_by_recurrent_customers
                results[time_span]['rest'] -= n_store_orders_by_recurrent_customers
            for vertical in verticals:
                vertical_orders_df = orders_df[orders_df['order_vertical'] == vertical]
                n_vertical_orders_by_recurrent_customers = int(vertical_orders_df['customer_id'].isin(customers_df['customer_id']).sum())
                results[time_span][vertical] = n_vertical_orders_by_recurrent_customers
                results[time_span]['rest'] -= n_vertical_orders_by_recurrent_customers
    return results



print(filter_and_count_rc_orders(loaded_recurrent_customers, loaded_orders, ["McDonald's",'KFC'], ['QCommerce']))


results = filter_and_count_rc_orders(loaded_recurrent_customers, loaded_orders, ["McDonald's",'KFC'], ['QCommerce'])

# Extracting the data
dates = list(results.keys())
months = [pd.to_datetime(date.split(' to ')[0]).strftime('%b %y') for date in dates]
totals = [results[date]['total'] for date in dates]

# Sort the data by dates in ascending order
sorted_indices = np.argsort([pd.to_datetime(date.split(' to ')[0]) for date in dates])
months = [months[i] for i in sorted_indices]
totals = [totals[i] for i in sorted_indices]
results = {dates[i]: results[dates[i]] for i in sorted_indices}

# Extracting categories dynamically
categories = set()
for value in results.values():
    categories.update(value.keys())
categories.discard('total')
categories.discard('rest')
categories = list(categories)

# Extracting values for each category
category_values = {category: [results[date].get(category, 0) for date in results.keys()] for category in categories}
rest = [results[date]['rest'] for date in results.keys()]

# Calculate percentages
category_percentages = {category: [value / total * 100 for value, total in zip(values, totals)] for category, values in category_values.items()}
rest_pct = [r / t * 100 for r, t in zip(rest, totals)]

# Plotting the stacked bar chart
fig, ax = plt.subplots(figsize=(12, 6))

# Stacked bars
bottoms = np.zeros(len(dates))
bars = {}
for category in categories:
    bars[category] = ax.bar(months, category_values[category], bottom=bottoms, label=category)
    bottoms += category_values[category]

bars['rest'] = ax.bar(months, rest, bottom=bottoms, label='Rest')

# Adding labels and title
# ax.set_xlabel('Months')
ax.set_title('Recurrent customers orders')
ax.legend()

# Adding percentages inside the bars
def add_labels(bars, percentages):
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_y() + height / 2,
            f'{pct:.1f}%',
            ha='center',
            va='center',
            color='white',
            fontsize=7,
            fontweight='bold'
        )

for category in categories:
    add_labels(bars[category], category_percentages[category])
add_labels(bars['rest'], rest_pct)

# Adding total values on top of the bars
for i, total in enumerate(totals):
    ax.text(
        i,
        bottoms[i] + rest[i],
        f'{total/1e6:.2f}M',
        ha='center',
        va='bottom',
        fontsize=8,
        # fontweight='bold'
    )

# Remove y-axis
ax.yaxis.set_visible(False)

# Display the chart
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('final_chart_white_background.png')