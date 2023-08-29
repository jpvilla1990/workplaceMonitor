tables = {
    "frames" : {
        "createTable" : """
CREATE TABLE frames (
    frameId INT AUTO_INCREMENT PRIMARY KEY,
    timestamp INT NOT NULL,
    timestampStrf VARCHAR(255) NOT NULL,
    pathImage VARCHAR(255) NOT NULL,
    pathImagePredict VARCHAR(255),
    personDetection BOOLEAN,
    actionDetection BOOLEAN
);
""",
        "checkTable" : """
SHOW TABLES LIKE 'frames'
""",
        "insertNewFrame" : """
INSERT INTO frames (timestamp, timestampStrf, pathImage, personDetection, actionDetection) VALUES ({timestamp}, '{timestampStrf}', '{pathImage}', {personDetection}, {actionDetection});
""",
        "getTimestampFromFrameId" : """
SELECT timestamp FROM frames WHERE frameId = {frameId};
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
        "updatePersonDetectionFromFrameId" : """
UPDATE frames SET personDetection = {personDetection} WHERE frameId = {frameId};
""",
        "updateActionDetectionFromFrameId" : """
UPDATE frames SET actionDetection = {actionDetection} WHERE frameId = {frameId};
""",
        "updateAnnotatedImagePathFromFrameId" : """
UPDATE frames SET pathImagePredict = '{pathImagePredict}' WHERE frameId = {frameId};
""",
    },
    "persons" : {
        "createTable" : """
CREATE TABLE persons (
    personId INT AUTO_INCREMENT PRIMARY KEY,
    pathVideoPredict VARCHAR(255),
    personCompleted BOOLEAN,
    idleClasification BOOLEAN
);
""",
        "checkTable" : """
SHOW TABLES LIKE 'persons'
""",
        "insertNewPerson" : """
INSERT INTO persons (personCompleted, idleClasification) VALUES (0, 0);
""",
        "updatePersonCompletedFromPersonId" : """
UPDATE persons SET personCompleted = {personCompleted} WHERE personId = {personId};
""",
        "updateVideoPathFromPersonId" : """
UPDATE persons SET pathVideoPredict = '{pathVideoPredict}' WHERE personId = {personId};
""",
        "updateIdleClasificationFromPersonId" : """
UPDATE persons SET idleClasification = {idleClasification} WHERE personId = {personId};
""",
        "getPersonsIdFromPersonCompleted" : """
SELECT personId FROM persons WHERE personCompleted = {personCompleted};
""",
        "getNewPerson" : """
SELECT personId FROM persons ORDER BY personId DESC LIMIT 1;
""",
        "getNextPersonIdVideoToStore" : """
SELECT personId FROM persons WHERE idleClasification = 1 AND personCompleted = 1 AND pathVideoPredict IS NULL LIMIT 1;
"""
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
        "getPersonIdFromObjectId" : """
SELECT personId FROM objects WHERE objectId = {objectId};
""",
        "getFrameIdFromPersonId" : """
SELECT frameId FROM objects WHERE personId = {personId} ORDER BY objectId DESC LIMIT 1;
""",
        "getCoordinatesByPersonId" : """
SELECT x_0, y_0, x_1, y_1 FROM objects WHERE personId = {personId};
""",
        "getObjectsIdFromPersonId" : """
SELECT x_0, y_0, x_1, y_1, frameId FROM objects WHERE personId = {personId};
""",
        "getFramesFromPersonId" : """
SELECT objectId FROM objects WHERE personId = {personId};
""",
        "getCoordinatesByObjectId" : """
SELECT x_0, y_0, x_1, y_1 FROM objects WHERE objectId = {objectId};
""",
    },
}

database = {
    "createDatabase" : "CREATE DATABASE ",
    "checkDatabase" : "SHOW DATABASES",
}