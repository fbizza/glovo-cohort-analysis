import matplotlib.pyplot as plt
import math


def plot_dictionaries(dict_of_dicts, max_plots_per_row=3, colors=None):

    main_keys = list(dict_of_dicts.keys())
    sub_keys = list(dict_of_dicts[main_keys[0]].keys())
    num_main_keys = len(main_keys)
    num_sub_keys = len(sub_keys)

    # default colors if not provided
    if colors is None:
        colors = plt.cm.get_cmap('tab10', num_main_keys).colors

    # Calculate the number of rows and columns
    num_rows = math.ceil(num_sub_keys / max_plots_per_row)
    num_cols = min(num_sub_keys, max_plots_per_row)

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(5 * num_cols, 5 * num_rows))

    if num_rows > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    for i, sub_key in enumerate(sub_keys):
        values = [dict_of_dicts[main_key][sub_key] for main_key in main_keys]
        axes[i].bar(range(num_main_keys), values, color=colors)
        axes[i].set_title(sub_key)
        axes[i].set_xticks(range(num_main_keys))
        axes[i].set_xticklabels(main_keys)

        # adjust y-axis to highlight differences
        min_val = min(values)
        max_val = max(values)
        lower = min_val - 0.1 * max_val if min_val > 0 else min_val - 0.1 * abs(min_val)
        upper = max_val + 0.1 * max_val
        axes[i].set_ylim(lower, upper)

        # annotate bars with their values
        for j, value in enumerate(values):
            if sub_key in ['prime_users_percentage', 'retention_percentage', 'negative_cm_orders_percentage', 'promo_percentage']:
                axes[i].text(j, value, f'{value*100:.2f}%', ha='center', va='bottom')
            else:
                axes[i].text(j, value, f'{value:.2f}', ha='center', va='bottom')

    # hide any unused subplots, useful if n_subplots is not multiple of 3
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # example usage
    dict_of_dicts = {
        'Dict1': {'avg_n_stores': 1.887, 'avg_order_frequency': 4.56, 'retention_percentage': 0.5731, 'avg_aov': 63.52, 'avg_cm': 1.13, 'negative_cm_orders_percentage': 0.2657, 'prime_users_percentage': 0.0202, 'promo_percentage': 0.43233},
        'Dict2': {'avg_n_stores': 2.496, 'avg_order_frequency': 5.124, 'retention_percentage': 0.5769, 'avg_aov': 68.93, 'avg_cm': 1.33, 'negative_cm_orders_percentage': 0.2399, 'prime_users_percentage': 0.0377, 'promo_percentage': 0.45925}
    }

    colors = ['blue', 'green']

    plot_dictionaries(dict_of_dicts, colors=colors)