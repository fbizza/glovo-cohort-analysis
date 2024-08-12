import extract_data, filter_and_count, plot

timeframe = 'weekly'
n_periods = 13
store_names = ["McDonald's", 'KFC']
verticals = ['QCommerce']

#extract_data.process_queries(timeframe, n_periods)
results = filter_and_count.filter_and_count_rc_orders(timeframe, store_names, verticals)
plot.plot_results(results, timeframe, save_plot=True, show_plot=True, print_results_to_console=True)