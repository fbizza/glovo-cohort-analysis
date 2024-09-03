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
        lower = 0.6  # bigger values to highlight small differences
        upper = 0.1
        max_val = max(values)
        axes[i].set_ylim(lower * max_val, max_val + upper * max_val)

        # annotate bars with their values
        for j, value in enumerate(values):
            axes[i].text(j, value, f'{value:.2f}', ha='center', va='bottom')

    # hide any unused subplots, useful if n_subplots is not multiple of 3
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # example usage
    dict_of_dicts = {
        'Dict1': {'avg_n_stores': 1.886, 'avg_order_frequency': 4.536, 'retention_rate': 57.19, 'avg_aov': 63.41, 'avg_cm': 1.04, 'negative_cm_orders_percentage': 0.289},
        'Dict2': {'avg_n_stores': 2.485, 'avg_order_frequency': 5.084, 'retention_rate': 57.53, 'avg_aov': 69.01, 'avg_cm': 1.22, 'negative_cm_orders_percentage': 0.263}
    }

    colors = ['blue', 'green']

    plot_dictionaries(dict_of_dicts, colors=colors)