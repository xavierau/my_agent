import pstats

p = pstats.Stats('profile_output.stats')
p.sort_stats('cumulative').print_stats(50)  # Adjust as needed
