import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import json

def plot_results(results, timeframe, save_plot=True, show_plot=True, print_results_to_console=True):

    if print_results_to_console:
        pretty_dict = json.dumps(results, indent=4)
        print(pretty_dict)

    dates = list(results.keys())

    if timeframe == 'monthly':
        periods = [pd.to_datetime(date.split(' to ')[0]).strftime('%b %y') for date in dates]
    else:
        periods = [pd.to_datetime(date.split(' to ')[0]).strftime('%d %b %y') for date in dates]

    totals = [results[date]['total'] for date in dates]
    sorted_indices = np.argsort([pd.to_datetime(date.split(' to ')[0]) for date in dates])
    periods = [periods[i] for i in sorted_indices]
    totals = [totals[i] for i in sorted_indices]
    results = {dates[i]: results[dates[i]] for i in sorted_indices}

    categories = set()
    for value in results.values():
        categories.update(value.keys())
    categories.discard('total')
    categories.discard('rest')
    categories = list(categories)

    category_values = {category: [results[date].get(category, 0) for date in results.keys()] for category in categories}
    rest = [results[date]['rest'] for date in results.keys()]
    category_percentages = {category: [value / total * 100 for value, total in zip(values, totals)] for category, values
                            in category_values.items()}
    rest_pct = [r / t * 100 for r, t in zip(rest, totals)]

    fig, ax = plt.subplots(figsize=(12, 6))
    bottoms = np.zeros(len(dates))
    bars = {}

    for category in categories:
        bars[category] = ax.bar(periods, category_values[category], bottom=bottoms, label=category)
        bottoms += category_values[category]

    bars['rest'] = ax.bar(periods, rest, bottom=bottoms, label='Rest')
    ax.set_title('Recurrent customers orders')
    ax.legend()

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


    for i, total in enumerate(totals):
        ax.text(
            i,
            bottoms[i] + rest[i],
            f'{total / 1e6:.2f}M' if timeframe == 'monthly' else f'{total / 1e3:.0f}k',
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight='bold'
        )

    ax.yaxis.set_visible(False)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_plot:
        current_date = datetime.now().strftime('%d_%m_%Y')
        filename = f'../figures/{timeframe}/{current_date}_export'
        plt.savefig(filename)

    if show_plot:
        plt.show()

def plot_promo_yes_no_results(results, timeframe, save_plot=True, show_plot=True, print_results_to_console=True):

    if print_results_to_console:
        pretty_dict = json.dumps(results, indent=4)
        print(pretty_dict)

    dates = list(results.keys())

    if timeframe == 'monthly':
        periods = [pd.to_datetime(date.split(' to ')[0]).strftime('%b %y') for date in dates]
    else:
        periods = [pd.to_datetime(date.split(' to ')[0]).strftime('%d %b %y') for date in dates]

    totals = [results[date]['total_orders'] for date in dates]
    sorted_indices = np.argsort([pd.to_datetime(date.split(' to ')[0]) for date in dates])
    periods = [periods[i] for i in sorted_indices]
    totals = [totals[i] for i in sorted_indices]
    results = {dates[i]: results[dates[i]] for i in sorted_indices}

    promo_orders = [results[date]['promo_orders'] for date in results.keys()]
    non_promo_orders = [results[date]['non_promo_orders'] for date in results.keys()]
    promo_percentages = [results[date]['promo_percentage'] for date in results.keys()]
    non_promo_percentages = [results[date]['non_promo_percentage'] for date in results.keys()]

    fig, ax = plt.subplots(figsize=(12, 6))
    bottoms = np.zeros(len(dates))

    bars_promo = ax.bar(periods, promo_orders, bottom=bottoms, label='Promo Orders')
    bottoms += promo_orders
    bars_non_promo = ax.bar(periods, non_promo_orders, bottom=bottoms, label='Non-Promo Orders')

    ax.set_title('Recurrent Customers Orders with Promo and Non-Promo')
    ax.legend()

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

    add_labels(bars_promo, promo_percentages)
    add_labels(bars_non_promo, non_promo_percentages)

    # Add total labels on top of the stacked bars
    for i, total in enumerate(totals):
        ax.text(
            i,
            bottoms[i] + non_promo_orders[i],  # Add non_promo_orders to get the top of the stack
            f'{total / 1e6:.2f}M' if timeframe == 'monthly' else f'{total / 1e3:.0f}k',
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight='bold'
        )

    ax.yaxis.set_visible(False)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_plot:
        current_date = datetime.now().strftime('%d_%m_%Y')
        filename = f'../figures/{timeframe}/{current_date}_export_promo_yes_no.png'
        plt.savefig(filename)

    if show_plot:
        plt.show()


def plot_results_prime_yes_no(results, timeframe, save_plot=True, show_plot=True, print_results_to_console=True):
    if print_results_to_console:
        pretty_dict = json.dumps(results, indent=4)
        print(pretty_dict)

    dates = list(results.keys())

    if timeframe == 'monthly':
        periods = [pd.to_datetime(date.split(' to ')[0]).strftime('%b %y') for date in dates]
    else:
        periods = [pd.to_datetime(date.split(' to ')[0]).strftime('%d %b %y') for date in dates]

    totals = [results[date]['total'] for date in dates]
    sorted_indices = np.argsort([pd.to_datetime(date.split(' to ')[0]) for date in dates])
    periods = [periods[i] for i in sorted_indices]
    totals = [totals[i] for i in sorted_indices]
    results = {dates[i]: results[dates[i]] for i in sorted_indices}

    promo_orders = [results[date][True] for date in results.keys()]
    non_promo_orders = [results[date][False] for date in results.keys()]
    promo_percentages = [results[date][True]/results[date]['total'] for date in results.keys()]
    non_promo_percentages = [results[date][False]/results[date]['total'] for date in results.keys()]

    fig, ax = plt.subplots(figsize=(12, 6))
    bottoms = np.zeros(len(dates))

    bars_promo = ax.bar(periods, promo_orders, bottom=bottoms, label='Prime Orders')
    bottoms += promo_orders
    bars_non_promo = ax.bar(periods, non_promo_orders, bottom=bottoms, label='Non-Prime Orders')

    ax.set_title('Recurrent Customers Orders Prime and Non-Prime')
    ax.legend()

    def add_labels(bars, percentages):
        for bar, pct in zip(bars, percentages):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + height / 2,
                f'{pct:.3f}%',
                ha='center',
                va='center',
                color='white',
                fontsize=7,
                fontweight='bold'
            )

    add_labels(bars_promo, promo_percentages)
    add_labels(bars_non_promo, non_promo_percentages)

    # Add total labels on top of the stacked bars
    for i, total in enumerate(totals):
        ax.text(
            i,
            bottoms[i] + non_promo_orders[i],  # Add non_promo_orders to get the top of the stack
            f'{total / 1e6:.2f}M' if timeframe == 'monthly' else f'{total / 1e3:.0f}k',
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight='bold'
        )

    ax.yaxis.set_visible(False)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_plot:
        current_date = datetime.now().strftime('%d_%m_%Y')
        filename = f'../figures/{timeframe}/{current_date}_export_prime_yes_no.png'
        plt.savefig(filename)

    if show_plot:
        plt.show()