-- populate_exp_perf_measures_am_5ptt_ix.sql
UPDATE expressway_performance_measures INNER JOIN Inrix_2019_cmp_exp_planning_time_idx_am ON expressway_performance_measures.tmc = Inrix_2019_cmp_exp_planning_time_idx_am.tmc SET expressway_performance_measures.am_5ptt_ix = [inrix_2019_cmp_exp_planning_time_idx_am].[pt_idx];