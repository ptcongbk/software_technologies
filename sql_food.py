
import sqlite3

def listDistinctiveBusiness():
    """
        List all businesses have at least 1 violation.
        Save the result to database
    """
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    dropPreviousViolationsCommand = """
        DROP TABLE IF EXISTS PreviousViolations;
    """
    cursor.execute(dropPreviousViolationsCommand)

    createPreviousViolationCommand = """
        CREATE TABLE PreviousViolations
        (
            FacilityName varchar(256),
            FacilityAddress varchar(256),
            FacilityCity varchar(256),
            FacilityZip varchar(20)
        );
    """
    cursor.execute(createPreviousViolationCommand)

    command = """
                SELECT DISTINCT i.FacilityName, i.FacilityAddress, i.FacilityCity, i.FacilityZip
                FROM Inspections i, Violations v
                WHERE i.SerialNumber = v.SerialNumber
                ORDER BY i.FacilityName
            """
    cursor.execute(command)
    facilities = cursor.fetchall()
    for facility in facilities:
        print(facility)

    insertCommand = """
                INSERT INTO PreviousViolations(FacilityName, FacilityAddress, FacilityCity, FacilityZip)
                SELECT DISTINCT i.FacilityName, i.FacilityAddress, i.FacilityCity, i.FacilityZip
                FROM inspections i, violations v
                WHERE i.SerialNumber = v.SerialNumber
                ORDER BY i.FacilityName
            """
    cursor.execute(insertCommand)
    connection.commit()
    connection.close()

def listBusinessWithCountedViolations():
    """
        List all businesses with counted violations
    """
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    ##Group by Facility and Count(*) to count all row
    command = """
                SELECT i.FacilityName, COUNT(*) as CountedViolation
                FROM Inspections i, Violations v
                WHERE i.SerialNumber = v.SerialNumber
                GROUP BY i.FacilityId
                ORDER BY COUNT(*)
            """
    cursor.execute(command)
    facilities = cursor.fetchall()
    for facility in facilities:
        print('Name: ',facility[0], ' - Counted: ', facility[1])
    connection.close()
    
if __name__ =="__main__":
    listDistinctiveBusiness()
    listBusinessWithCountedViolations()
