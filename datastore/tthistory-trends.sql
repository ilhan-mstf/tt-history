CREATE TABLE trends
(
woeid int,
duration int,
name varchar(255),
timestamp int
);

CREATE INDEX woeid_index
ON trends (woeid);

CREATE INDEX timestamp_index
ON trends (timestamp);

CREATE INDEX comp_index
ON trends (woeid, timestamp);

LOAD DATA INFILE '/var/lib/mysql-files/all_trends_2016_11_12.csv'
IGNORE INTO TABLE trends
CHARACTER SET UTF8
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

LOAD DATA INFILE '/var/lib/mysql-files/small.csv'
IGNORE INTO TABLE trends
CHARACTER SET UTF8
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

SELECT name, SUM(duration) FROM trends
WHERE woeid = 1
AND timestamp >= 1478898000
AND timestamp < 1478976120
GROUP BY name
ORDER BY SUM(duration) DESC;

SELECT woeid, name, SUM(duration) FROM trends
GROUP BY name
ORDER BY SUM(duration) DESC
LIMIT 5;

mysql> SELECT name, SUM(duration) FROM trends GROUP BY name ORDER BY SUM(duration) DESC LIMIT 5;
+------------------------------+---------------+
| name                         | SUM(duration) |
+------------------------------+---------------+
| Hayırlı Cumalar              |        179220 |
| #fenerinmaçıvar              |         64890 |
| #BeşiktaşınMaçıVar           |         59250 |
| #BugünGünlerdenGALATASARAY   |         53630 |
| Mutlu Pazarlar               |         50810 |
+------------------------------+---------------+
5 rows in set (3 min 50,76 sec)
