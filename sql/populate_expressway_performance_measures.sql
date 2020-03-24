-- populate_expressway_performance_measures.sql
-- This populates the expressway_performance_measures table with non-performance metrics data
-- culled from the Road Inventory and the INRIX 2019 TMC shapefile.
--
INSERT INTO expressway_performance_measures ( rid, tmc, from_meas, to_meas, distance, 
                                              route_id, route_num, road_name, direction, 
                                              seg_begin, seg_end, community )
SELECT  Inrix_2019_cmp_exp_roadinv_attrib.rid, 
        Inrix_2019_cmp_exp_roadinv_attrib.tmc, 
        Inrix_2019_cmp_exp_roadinv_attrib.from_meas, 
        Inrix_2019_cmp_exp_roadinv_attrib.to_meas, 
        Inrix_2019_cmp_exp_avg_length.avg_length, 
        Inrix_2019_cmp_exp_roadinv_attrib.route_id,
        Inrix_2019_cmp_exp_roadinv_attrib.route_num, 
        Inrix_2019_cmp_exp_roadinv_attrib.road_name, 
        Inrix_2019_cmp_exp_roadinv_attrib.direction, 
        Inrix_2019_cmp_exp_roadinv_attrib.seg_begin, 
        Inrix_2019_cmp_exp_roadinv_attrib.seg_end, 
        Inrix_2019_cmp_exp_roadinv_attrib.community
FROM Inrix_2019_cmp_exp_roadinv_attrib 
INNER JOIN Inrix_2019_cmp_exp_avg_length 
ON Inrix_2019_cmp_exp_roadinv_attrib.tmc = Inrix_2019_cmp_exp_avg_length.tmc;