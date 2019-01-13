import sqlite3
import datetime
import dateutil
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import openpyxl
from scipy.interpolate import spline

def getMinMaxDate():
    """ Get min and max date of inspections in DB """
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    command ="""
        SELECT MIN(ActivityDate) as MinDate, MAX(ActivityDate) as MaxDate
        FROM Inspections
    """
    cursor.execute(command)
    result = cursor.fetchone()
    connection.close()
    return result

def violationsInHighestAndLowestPCs(periods):
    """
        Get postal codes with highest and lowest violations and visualize the number of violations per month.

            periods: timespan to draw the plot.
    """
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()

    #Get postal codes with highest and lowest violations first(for lowest I choose 1 in many results)
    command = """
                SELECT i.FacilityZip, COUNT(*) as CountedViolation
                FROM Inspections i, Violations v
                WHERE i.SerialNumber = v.SerialNumber
                GROUP BY i.FacilityZip
                ORDER BY COUNT(*) DESC
            """
    cursor.execute(command)
    violationByZips = cursor.fetchall()
    highestViolationZip = violationByZips[0][0] #1st item
    lowestViolationZip = violationByZips[-1][0] #last item
    
    #Get violation counts by month for 2 above postal codes
    statisticByMonthCommand ="""
                SELECT STRFTIME('%m/%Y', i.ActivityDate) AS Month, i.FacilityZip as PostalCode, COUNT(*) as Total
                FROM Inspections i, Violations v
                WHERE i.SerialNumber = v.SerialNumber AND i.FacilityZip IN ('"""+ highestViolationZip +"""','"""+ lowestViolationZip+"""')
                GROUP BY STRFTIME('%m/%Y', i.ActivityDate), i.FacilityZip
                ORDER BY i.ActivityDate
            """
    cursor.execute(statisticByMonthCommand)
    statisticByMonths = cursor.fetchall()
    connection.close()

    #draw the chart with 2 subplots for better comparison
    highestDatas = list()
    lowestDatas = list()
    for period in periods:
        highestData = next((x for x in statisticByMonths if x[1] == highestViolationZip and x[0] == period), (period,highestViolationZip,0))
        highestDatas.append(highestData[2])
        lowestData = next((x for x in statisticByMonths if x[1] == lowestViolationZip and x[0] == period), (period,lowestViolationZip,0))
        lowestDatas.append(lowestData[2])
    
    plt.figure(1)
    bar_width = 0.35
    opacity = 0.4
    plt.subplot(211) 
    plt.title('Violations per month in postal code ' + highestViolationZip, fontsize=16, fontweight='bold')
    plt.bar(periods, highestDatas, bar_width, alpha=opacity, color='b', label=highestViolationZip)
    plt.xlabel('')
    plt.xticks(rotation=70)
    plt.ylabel('Total')

    plt.subplot(212) 
    plt.title('Violations per month in postal code ' + lowestViolationZip, fontsize=16, fontweight='bold')
    plt.bar(periods, lowestDatas, bar_width, alpha=opacity, color='r', label=lowestViolationZip)
    plt.xlabel('Month')
    plt.xticks(rotation=70)
    plt.ylabel('Total')
    plt.yticks(np.arange(2), ('0', '1'))
    plt.show()

def averageByMonthInCali(periods):
    """
        Get average violations per month in Cali.

            periods: timespan to draw the plot.
    """
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    #Get average violations in Cali
    statisticByMonthCommand ="""
                SELECT STRFTIME('%m/%Y', i.ActivityDate) AS Month, COUNT(DISTINCT i.FacilityZip) as TotalPostalCode, COUNT(*) as Total
                FROM Inspections i, Violations v
                WHERE i.SerialNumber = v.SerialNumber
                GROUP BY STRFTIME('%m/%Y', i.ActivityDate)
                ORDER BY i.ActivityDate
            """
    cursor.execute(statisticByMonthCommand)
    statisticByMonths = cursor.fetchall()
    connection.close()

    #draw the trending chart in California
    indexes = np.arange(len(periods))
    plt.figure(2)
    datas = list()
    for period in periods:
        data = next((x for x in statisticByMonths if x[0] == period), (period,1,0))
        datas.append(data[2]/data[1]) 
    plt.title('The Average Violations in California')
    plt.plot(indexes, datas, 'r-')
    plt.plot(indexes, datas, 'r-o')
    plt.xlabel('Month')
    plt.xticks(indexes, periods)
    plt.xticks(rotation=70)
    plt.ylabel('Total')
    plt.axis([indexes[0], indexes[-1],40,60])
    plt.show()

def compareTwoBrands(periods, brand1, brand2):
    """
        Get average violations per month in Cali.

            periods: timespan to draw the plot.
            brand1: Brand 1
            brand2: Brand 2
    """
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    brand1StatisticCommand = """
        SELECT STRFTIME('%m/%Y', i.ActivityDate) AS Month, COUNT(DISTINCT FacilityId) as TotalStore, COUNT(*) as Total
            FROM Inspections i, Violations v
            WHERE i.SerialNumber = v.SerialNumber AND FacilityName LIKE '%"""+ brand1 +"""%'
            GROUP BY STRFTIME('%m/%Y', i.ActivityDate)
            ORDER BY i.ActivityDate
    """
    cursor.execute(brand1StatisticCommand)
    brand1StatisticByMonths = cursor.fetchall()

    brand2StatisticCommand = """
        SELECT STRFTIME('%m/%Y', i.ActivityDate) AS Month, COUNT(DISTINCT FacilityId) as TotalStore, COUNT(*) as Total
            FROM Inspections i, Violations v
            WHERE i.SerialNumber = v.SerialNumber AND FacilityName LIKE '%"""+ brand2 +"""%'
            GROUP BY STRFTIME('%m/%Y', i.ActivityDate)
            ORDER BY i.ActivityDate
    """
    cursor.execute(brand2StatisticCommand)
    brand2StatisticByMonths = cursor.fetchall()
    connection.close()

    #draw the charts
    brand1Datas = list()
    brand2Datas = list()
    for period in periods:
        brand1Data = next((x for x in brand1StatisticByMonths if x[0] == period), (period,brand2,0))
        brand1Datas.append(brand1Data[2]/brand1Data[1])
        brand2Data = next((x for x in brand2StatisticByMonths if x[0] == period), (period,brand2,0))
        brand2Datas.append(brand2Data[2]/brand2Data[1])
   

    indexes = np.arange(len(periods))
    #Make data smoothier to create better visualization
    x_smooth = np.linspace(indexes.min(), indexes.max(), 450)
    brand1SmoothDatas = spline(indexes, brand1Datas, x_smooth)
    brand2SmoothDatas = spline(indexes, brand2Datas, x_smooth)

    plt.figure(3)
    plt.plot(x_smooth, brand1SmoothDatas, '#ff9999', label=brand1)
    plt.fill_between(x_smooth, 0, brand1SmoothDatas, color='red', alpha=.3)
    plt.plot(x_smooth, brand2SmoothDatas, '#998f5b', label=brand2)
    plt.fill_between(x_smooth, 0, brand2SmoothDatas, color='green', alpha=.3)
    plt.xlabel('Month')
    plt.xticks(rotation=70)
    plt.ylabel('Total')
    plt.xticks(indexes, periods)
    plt.legend(loc=1)
    plt.tight_layout()
    plt.axis([indexes[0], indexes[-1],0,6])
    plt.show()

def listFoodViolations():
    """Print the list violations's code and description related with food"""
    connection = sqlite3.connect("inspection.db")
    cursor = connection.cursor()
    violationCommand = """
        SELECT DISTINCT ViolationCode, Description
        FROM Violations
        ORDER BY ViolationCode
    """
    cursor.execute(violationCommand)
    violations = cursor.fetchall()
    connection.close()
    
    foodViolations = [i for i in violations if re.search('food', i[1], re.IGNORECASE)]
    for violation in foodViolations:
        print(violation)
        
    #Save to file to append to appendix
    if os.path.exists("FoodViolations.xlsx"):
        os.remove("FoodViolations.xlsx")
    ws_name = r"FoodViolations.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Violations"
    header = [u'Code', u'Description']
    ws.append(header)
    for violation in foodViolations:
      ws.append(violation)
    wb.save(ws_name)


if __name__ =="__main__":
    #get periods to draw the plots
    minMaxDate = getMinMaxDate()
    minDate = datetime.datetime.strptime(minMaxDate[0],'%Y-%m-%d %H:%M:%S.%f')
    maxDate = datetime.datetime.strptime(minMaxDate[1],'%Y-%m-%d %H:%M:%S.%f')
    periods = list()
    while minDate <= maxDate:
        periods.append(minDate.strftime("%m/%Y"))
        minDate = minDate + dateutil.relativedelta.relativedelta(months=+1)

    #show statistic by month for 2 special zip codes
    violationsInHighestAndLowestPCs(periods)

    #show average violation in California
    averageByMonthInCali(periods)

    #compare between McDonald and Burger King
    compareTwoBrands(periods,"McDonald","Burger King")

    #statistic food violations
    listFoodViolations()