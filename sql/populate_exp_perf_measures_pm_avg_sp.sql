-- populate_exp_perf_measures_pm_avg_sp.sql
UPDATE expressway_performance_measures INNER JOIN Inrix_2019_cmp_exp_avg_speed_all_pm ON expressway_performance_measures.tmc = Inrix_2019_cmp_exp_avg_speed_all_pm.tmc SET expressway_performance_measures.pm_avg_sp = [Inrix_2019_cmp_exp_avg_speed_all_pm].[avg_speed];