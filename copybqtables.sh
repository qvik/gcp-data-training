#!/bin/bash
bq mk google_analytics_sample
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
do
  bq cp bigquery-public-data:google_analytics_sample.ga_sessions_201707$i google_analytics_sample.ga_sessions_201707$i
done
