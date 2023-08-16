tables = {
    "frames" : {
        "createTable" : """
CREATE TABLE frames (
    frameId INT AUTO_INCREMENT PRIMARY KEY,
    timestamp INT NOT NULL,
    timestampStrf VARCHAR(255) NOT NULL,
    pathImage VARCHAR(255) NOT NULL,
    personDetection BOOLEAN,
    actionDetection BOOLEAN
);
""",
        "checkTable" : """
SHOW TABLES LIKE 'frames'
""",
        "insertNewFrame" : """
INSERT INTO frames (timestamp, timestampStrf, pathImage, personDetection) VALUES ({timestamp}, '{timestampStrf}', '{pathImage}', {personDetection});
""",
        "getFrameIdLastPersonPrediction" : """
SELECT frameId FROM frames WHERE personDetection = 0 ORDER BY frameId LIMIT 1;
""",
        "getFrameIdLastActionPrediction" : """
SELECT frameId FROM frames WHERE actionDetection = 0 ORDER BY frameId LIMIT 1;
""",
        "getImagePathFromFrameId" : """
SELECT pathImage FROM frames WHERE frameId = {frameId};
""",
        "updateImagePathFromFrameId" : """
UPDATE frames SET personDetection = {personDetection} WHERE frameId = {frameId};
""",
    },
    "persons" : {
        "createTable" : """
CREATE TABLE persons (
    personId INT AUTO_INCREMENT PRIMARY KEY,
    personCompleted BOOLEAN
);
""",
        "checkTable" : """
SHOW TABLES LIKE 'persons'
""",
        "insertNewPerson" : """
INSERT INTO persons (personCompleted) VALUES (0);
""",
        "updatePersonCompletedFromPersonId" : """
UPDATE persons SET personCompleted = {personCompleted} WHERE personId = {personId};
""",
        "getPersonsIdFromPersonCompleted" : """
SELECT personId FROM persons WHERE personCompleted = {personCompleted};
""",
    },
    "objects" : {
        "createTable" : """
CREATE TABLE objects (
    objectId INT AUTO_INCREMENT PRIMARY KEY,
    x_0 INT NOT NULL,
    y_0 INT NOT NULL,
    x_1 INT NOT NULL,
    y_1 INT NOT NULL,
    frameId INT NOT NULL,
    personId INT,
    FOREIGN KEY (personId) REFERENCES persons (personId),
    FOREIGN KEY (frameId) REFERENCES frames (frameId)
);
""",
        "checkTable" : """
SHOW TABLES LIKE 'objects'
""",
        "insertNewObject" : """
INSERT INTO objects (frameId, x_0, y_0, x_1, y_1) VALUES ({frameId}, {x_0}, {y_0}, {x_1}, {y_1});
""",
        "updatePersonIdFromObjectId" : """
UPDATE objects SET personId = {personId} WHERE objectId = {objectId};
""",
        "getObjectsIdFromFrameId" : """
SELECT objectId FROM objects WHERE frameId = {frameId};
""",
    },
}

database = {
    "createDatabase" : "CREATE DATABASE ",
    "checkDatabase" : "SHOW DATABASES",
}