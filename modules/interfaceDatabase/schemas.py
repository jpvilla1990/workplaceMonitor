tables = {
    "frames" : {
        "createTable" : """
CREATE TABLE frames (
    timestamp INT NOT NULL PRIMARY KEY,
    timeStampStrf VARCHAR(255) NOT NULL,
    pathImage VARCHAR(255) NOT NULL,
    personDetection BOOLEAN
);
""",
        "checkTable" : """
SHOW TABLES LIKE 'frames'
""",
        "insertNewFrame" : """
INSERT INTO frames (timeStamp, timeStampStrf, pathImage, personDetection) VALUES (%s, %s, %s, %s)
""",
        "getIdLastPrediction" : """
SELECT timeStamp FROM frames WHERE personDetection = 0 LIMIT 1;
"""
    },
}

database = {
    "createDatabase" : "CREATE DATABASE ",
    "checkDatabase" : "SHOW DATABASES",
}