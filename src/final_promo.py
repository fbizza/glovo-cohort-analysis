import extract_data, filter_and_count, plot, extract_data_promo, filter_and_count

timeframe = 'monthly'
n_periods = 13
store_names = ["McDonald's", 'KFC']
verticals = ['QCommerce']

# extract_data_promo.process_queries(timeframe, n_periods)
results = filter_and_count.filter_and_count_promo_yes_no(timeframe, store_names, verticals)
plot.plot_promo_yes_no_results(results, timeframe, save_plot=True, show_plot=True, print_results_to_console=True)
