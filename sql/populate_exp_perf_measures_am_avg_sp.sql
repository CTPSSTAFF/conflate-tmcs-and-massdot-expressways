-- populate_exp_perf_measures_am_avg_sp.sql
UPDATE expressway_performance_measures INNER JOIN Inrix_2019_cmp_exp_avg_speed_all_am ON expressway_performance_measures.tmc = Inrix_2019_cmp_exp_avg_speed_all_am.tmc SET expressway_performance_measures.am_avg_sp = [Inrix_2019_cmp_exp_avg_speed_all_am].[avg_speed];
