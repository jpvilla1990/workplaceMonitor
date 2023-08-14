tables = {
    "frames" : {
        "createTable" : """
CREATE TABLE frames (
    timestamp INT NOT NULL PRIMARY KEY,
    timestampStrf VARCHAR(255) NOT NULL,
    pathImage VARCHAR(255) NOT NULL,
    personDetection BOOLEAN
);
""",
        "checkTable" : """
SHOW TABLES LIKE 'frames'
""",
        "insertNewFrame" : """
INSERT INTO frames (timestamp, timestampStrf, pathImage, personDetection) VALUES (%s, %s, %s, %s)
""",
        "getIdLastPrediction" : """
SELECT timestamp FROM frames WHERE personDetection = 0 LIMIT 1;
""",
        "getImagePathFromTimestamp" : """
SELECT pathImage FROM frames WHERE timestamp = {timestamp};
""",
    },
}

database = {
    "createDatabase" : "CREATE DATABASE ",
    "checkDatabase" : "SHOW DATABASES",
}