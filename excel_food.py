import openpyxl
import os
import sqlite3
import numpy as np

def getViolationList():
  """
    Get violations list from db
  """
  connection = sqlite3.connect("inspection.db")
  cursor = connection.cursor()
  command = """
              SELECT v.ViolationCode, v.Description, COUNT(*) as Counted
              FROM Violations v
              GROUP BY v.ViolationCode
              ORDER BY COUNT(*) DESC
          """
  cursor.execute(command)
  violations = cursor.fetchall()
  connection.close()
  return violations

def saveViolationToFile(violations):
  """
    Save violations to file
  """
  if os.path.exists("ViolationTypes.xlsx"):
    os.remove("ViolationTypes.xlsx")
  ws_name = r"ViolationTypes.xlsx"
  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = "Violations Types"
  header = [u'Code', u'Description', u'Count']
  ws.append(header)
  total = 0
  for violation in violations:
      ws.append(violation)
      total += violation[2]
  ws.append(['', u'Total Violations',total])
  wb.save(ws_name)



if __name__ =="__main__":
  violations = getViolationList()
  saveViolationToFile(violations)

