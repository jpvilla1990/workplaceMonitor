tables = {
    "frames" : {
        "createTable" : """
CREATE TABLE frames (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    timeStamp VARCHAR(255) NOT NULL,
    pathImage VARCHAR(255) NOT NULL,
    personDetection BOOLEAN,
    x_0 INT,
    y_0 INT,
    x_1 INT,
    y_2 INT
);
""",
        "checkTable" : """
SHOW TABLES LIKE 'frames'
""",
        "insertNewFrame" : """
INSERT INTO frames (timeStamp, pathImage, personDetection) VALUES (%s, %s, %s)
""",
    },
}

database = {
    "createDatabase" : "CREATE DATABASE ",
    "checkDatabase" : "SHOW DATABASES",
}