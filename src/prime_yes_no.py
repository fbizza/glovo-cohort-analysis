import extract_data, filter_and_count, plot

timeframe = 'monthly'
n_periods = 13
bool = [True, False]

#extract_data.process_queries(timeframe, n_periods)
results = filter_and_count.filter_and_count_rc_orders_prime_yes_no(timeframe, bool)
plot.plot_results_prime_yes_no(results, timeframe, save_plot=True, show_plot=True, print_results_to_console=True)