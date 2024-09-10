import matplotlib.pyplot as plt
import math

def plot_dictionaries(dict_of_dicts, max_plots_per_row=3, max_plots_per_page=6, colors=None):
    main_keys = list(dict_of_dicts.keys())
    sub_keys = list(dict_of_dicts[main_keys[0]].keys())
    num_main_keys = len(main_keys)
    num_sub_keys = len(sub_keys)

    # default colors if not provided
    if colors is None:
        colors = plt.colormaps['tab10'].colors

    # Calculate the number of pages
    num_pages = math.ceil(num_sub_keys / max_plots_per_page)

    for page in range(num_pages):
        start_idx = page * max_plots_per_page
        end_idx = min(start_idx + max_plots_per_page, num_sub_keys)
        current_sub_keys = sub_keys[start_idx:end_idx]

        num_rows = math.ceil(len(current_sub_keys) / max_plots_per_row)
        num_cols = min(len(current_sub_keys), max_plots_per_row)

        fig, axes = plt.subplots(num_rows, num_cols, figsize=(3 * num_cols, 3 * num_rows))

        # Ensure axes is always a list
        if num_rows > 1 or num_cols > 1:
            axes = axes.flatten()
        else:
            axes = [axes]

        for i, sub_key in enumerate(current_sub_keys):
            values = [dict_of_dicts[main_key][sub_key] for main_key in main_keys]
            axes[i].bar(range(num_main_keys), values, color=colors)
            axes[i].set_title(sub_key)
            axes[i].set_xticks(range(num_main_keys))
            axes[i].set_xticklabels(main_keys)

            # adjust y-axis to highlight differences
            min_val = min(values)
            max_val = max(values)
            lower = min_val - 0.2 * max_val if min_val > 0 else min_val - 0.1 * abs(min_val)
            upper = max_val + 0.2 * max_val
            axes[i].set_ylim(lower, upper)

            # annotate bars with their values
            for j, value in enumerate(values):
                if sub_key in ['second_order_retention', 'negative_com_orders', 'prime_users_conversion', 'retention_percentage', 'negative_cm_orders'] or ('promo' in sub_key):
                    axes[i].text(j, value, f'{value*100:.2f}%', ha='center', va='bottom')
                else:
                    axes[i].text(j, value, f'{value:.2f}', ha='center', va='bottom')

        # hide any unused subplots, useful if n_subplots is not multiple of max_plots_per_row
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # example usage
    dict_of_dicts = {
        'Dict1': {'5y_lto': 16.22171139995639,
                 'avg_aov': 62.36,
                 'avg_cm': 1.1,
                 'avg_n_stores': 1.876,
                 'avg_order_frequency': 4.47,
                 'basket_discount_promo_orders': 0.0036,
                 'flat_delivery_promo_orders': 0.008,
                 'free_delivery_promo_orders': 0.0234,
                 'mktg_promo_code_promo_orders': 0.1014,
                 'negative_cm_orders': 0.2691,
                 'percentage_discount_promo_orders': 0.0425,
                 'prime_promo_orders': 0.0336,
                 'prime_users_conversion': 0.0208,
                 'second_order_retention': 0.5691,
                 'segmentation_promo_orders': 0.0581,
                 'two_for_one_promo_orders': 0.005},
        'Dict2': {'5y_lto': 17.104947406230792,
                 'avg_aov': 67.29,
                 'avg_cm': 1.3,
                 'avg_n_stores': 2.436,
                 'avg_order_frequency': 4.844,
                 'basket_discount_promo_orders': 0.0059,
                 'flat_delivery_promo_orders': 0.0314,
                 'free_delivery_promo_orders': 0.0414,
                 'mktg_promo_code_promo_orders': 0.0426,
                 'negative_cm_orders': 0.2083,
                 'percentage_discount_promo_orders': 0.0797,
                 'prime_promo_orders': 0.0545,
                 'prime_users_conversion': 0.0258,
                 'second_order_retention': 0.5716,
                 'segmentation_promo_orders': 0.0508,
                 'two_for_one_promo_orders': 0.0092},
        'Dict3': {'5y_lto': 18.436153288870234,
                 'avg_aov': 69.0,
                 'avg_cm': 1.33,
                 'avg_n_stores': 2.491,
                 'avg_order_frequency': 5.238,
                 'basket_discount_promo_orders': 0.0059,
                 'flat_delivery_promo_orders': 0.0185,
                 'free_delivery_promo_orders': 0.0412,
                 'mktg_promo_code_promo_orders': 0.0419,
                 'negative_cm_orders': 0.2469,
                 'percentage_discount_promo_orders': 0.1151,
                 'prime_promo_orders': 0.071,
                 'prime_users_conversion': 0.039,
                 'second_order_retention': 0.5806,
                 'segmentation_promo_orders': 0.0466,
                 'two_for_one_promo_orders': 0.0083}

    }

    # colors = ['blue', 'green']

    plot_dictionaries(dict_of_dicts)