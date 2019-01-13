import sqlite3
import openpyxl
from datetime import datetime

def createTable():
    """
        Drop old tables if they are existed. Create 2 related tables to store data from excel
    """

    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    dropInspectionIfExistCommand = """
        DROP TABLE IF EXISTS Inspections;
    """
    cursor.execute(dropInspectionIfExistCommand)
    dropViolationIfExistCommand = """
        DROP TABLE IF EXISTS Violations;
    """
    cursor.execute(dropViolationIfExistCommand)

    createInpsectionCommand = """
        CREATE TABLE Inspections
        (
            ActivityDate datetime,
            EmployeeId varchar(50) NOT NULL,
            FacilityAddress varchar(256),
            FacilityCity varchar(256),
            FacilityId varchar(10),
            FacilityName varchar(256),
            FacilityState varchar(10),
            FacilityZip varchar(20),
            Grade varchar(5),
            OwnerId varchar(20),
            OwnerName varchar(256),
            PEDescription varchar(256),
            ProgramElementPE int,
            ProgramName varchar(256),
            ProgramStatus varchar(20),
            RecordId varchar(20),
            Score int,
            SerialNumber varchar(10),
            ServiceCode int,
            ServiceDescription varchar(30),
            CONSTRAINT PK_Inspections PRIMARY KEY (SerialNumber)
        );
    """
    cursor.execute(createInpsectionCommand)
   
    createViolationCommand = """
        CREATE TABLE Violations
        (
            Points int,
            SerialNumber varchar(10),
            ViolationCode varchar(5),
            Description varchar(256),
            Status varchar(20),  
            CONSTRAINT PK_Violations PRIMARY KEY (SerialNumber,ViolationCode) 
            CONSTRAINT FK_SerialNumber FOREIGN KEY(SerialNumber) REFERENCES Inspections(SerialNumber)  
        );
    """
    
    cursor.execute(createViolationCommand)
    connection.close()

def importInspections():
    """
        Import data from inspections file
    """
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    wb = openpyxl.load_workbook("inspections.xlsx")
    ws = wb["inspections"]
    datas = []
    for i, row in enumerate(ws):
        data = []
        if i == 0:
            continue
        for cell in row:
            if type(cell.value) is datetime:
                data.append(cell.value.strftime("%Y-%m-%d %H:%M:%S.%f"))
            else:
                data.append(cell.value)
        datas.append(data)
    insQuery = '''INSERT INTO Inspections(ActivityDate,EmployeeId,FacilityAddress,FacilityCity,FacilityId,FacilityName,FacilityState,FacilityZip,Grade,OwnerId,OwnerName,PEDescription,ProgramElementPE,ProgramName,ProgramStatus,RecordId,Score,SerialNumber,ServiceCode,ServiceDescription)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    cursor.executemany(insQuery, datas)
    connection.commit()
    connection.close()


def importViolations():
    """
        Import data from violations file.
    """
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    wb = openpyxl.load_workbook("violations.xlsx")
    ws = wb["violations"]
    datas = []
    #cursor.execute("PRAGMA foreign_keys = ON;")
    for i, row in enumerate(ws):
        data = []
        if i == 0:
            continue
        for cell in row:
            data.append(cell.value)
        datas.append(data)
    insQuery = '''INSERT OR IGNORE INTO Violations(Points,SerialNumber,ViolationCode,Description,Status)
                  VALUES(?,?,?,?,?)'''
    cursor.executemany(insQuery, datas)

    cursor.execute("DELETE FROM Inspections WHERE SerialNumber NOT IN (SELECT SerialNumber FROM Violations);")
    connection.commit()
    connection.close()


if __name__ =="__main__":
    print('Create table')
    createTable()
    print('Import data for inspections')
    importInspections()
    print('Import data for violations')
    importViolations()