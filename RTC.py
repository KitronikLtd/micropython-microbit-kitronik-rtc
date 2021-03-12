from microbit import *

class KitronikRTC:
    initalised = False
    CHIP_ADDRESS = 0x6F 	
    RTC_SECONDS_REG = 0x00		
    RTC_MINUTES_REG = 0x01		
    RTC_HOURS_REG = 0x02			
    RTC_WEEKDAY_REG = 0x03		
    RTC_DAY_REG = 0x04			
    RTC_MONTH_REG = 0x05			
    RTC_YEAR_REG = 0x06			
    RTC_CONTROL_REG = 0x07		
    RTC_OSCILLATOR_REG = 0x08 	
    RTC_PWR_UP_MINUTE_REG = 0x1C  
    START_RTC = 0x80
    STOP_RTC = 0x00
    ENABLE_BATTERY_BACKUP = 0x08
    currentSeconds = 0			
    currentMinutes = 0
    currentHours = 0
    currentWeekDay = 0
    currentDay = 0
    currentMonth = 0
    currentYear = 0  		
    
    def init(self):
        i2c.init(freq=100000, sda=pin20, scl=pin19)
        writeBuf = bytearray(2)
        readBuf = bytearray(1)
        readCurrentSeconds = 0
        readWeekDayReg = 0
        writeBuf[0] = self.RTC_SECONDS_REG
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        readBuf = i2c.read(self.CHIP_ADDRESS, 1, False)
        readCurrentSeconds = readBuf[0]
        writeBuf[0] = self.RTC_CONTROL_REG
        writeBuf[1] = 0x43
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_WEEKDAY_REG
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        readBuf = i2c.read(self.CHIP_ADDRESS, 1, False)
        readWeekDayReg = readBuf[0]
        writeBuf[0] = self.RTC_WEEKDAY_REG
        writeBuf[1] = self.ENABLE_BATTERY_BACKUP | readWeekDayReg
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.START_RTC | readCurrentSeconds
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        self.initalised = True

    def decToBcd(self, decNumber):
        tens = decNumber // 10
        units = decNumber % 10
        bcdNumber = (tens << 4) | units
        return bcdNumber
        
    def readValue(self): 
        if self.initalised is False:
            self.init(self)
        writeBuf = bytearray(1)
        readBuf = bytearray(7)
        self.readCurrentSeconds = 0
        writeBuf[0] = self.RTC_SECONDS_REG
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        readBuf = i2c.read(self.CHIP_ADDRESS, 7, False)
        self.currentSeconds = (((readBuf[0] & 0x70) >> 4) * 10) + (readBuf[0] & 0x0F)
        self.currentMinutes = (((readBuf[1] & 0x70) >> 4) * 10) + (readBuf[1] & 0x0F)
        self.currentHours = (((readBuf[2] & 0x30) >> 4) * 10) + (readBuf[2] & 0x0F)
        self.currentWeekDay = readBuf[3]
        self.currentDay = (((readBuf[4] & 0x30) >> 4) * 10) + (readBuf[4] & 0x0F)
        self.currentMonth =(((readBuf[5] & 0x10) >> 4) * 10) + (readBuf[5] & 0x0F) 
        self.currentYear = (((readBuf[6] & 0xF0) >> 4) * 10) + (readBuf[6] & 0x0F)
        
    def setTime(self, setHours, setMinutes, setSeconds): 
        if self.initalised is False:
            self.init(self)	
        bcdHours = self.decToBcd(self, setHours)
        bcdMinutes = self.decToBcd(self, setMinutes)
        bcdSeconds = self.decToBcd(self, setSeconds)
        writeBuf = bytearray(2)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.STOP_RTC
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_HOURS_REG
        writeBuf[1] = bcdHours	
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_MINUTES_REG
        writeBuf[1] = bcdMinutes
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.START_RTC | bcdSeconds
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)

    def readTimeAndDate(self): 
        if self.initalised is False:
            self.init(self)
        self.readValue(self)
        if self.currentHours <= 9:
            hourString = "0" + str(self.currentHours)
        else:
            hourString = str(self.currentHours)
        if self.currentHours <= 9:
            minuteString = "0" + str(self.currentMinutes)
        else:
            minuteString = str(self.currentMinutes)
        if self.currentSeconds <= 9:
            secString = "0" + str(self.currentSeconds)
        else:
            secString = str(self.currentSeconds)
        timeAndDate = "" + hourString + ":" + minuteString + ":" + secString + "   " + str(self.currentDay) + "/" + str(self.currentMonth) + "/" + str(self.currentYear)
        return timeAndDate

    def setDate(self, setDay, setMonth, setYear): 
        if self.initalised is False:
            self.init(self)
        leapYearCheck = 0
        writeBuf = bytearray(2)
        readReqBuf = bytearray(1)
        readBuf = bytearray(1)
        if setMonth is 4 or 6 or 9 or 11:
            if setDay is 30:
                setDay = 30
        if setMonth is 2 and setDay is 29:
            leapYearCheck = setYear % 4
            if leapYearCheck is 0:
                setDay = 29
            else:
                setDay = 28
        bcdDay = self.decToBcd(self, setDay)
        bcdMonths = self.decToBcd(self, setMonth)
        bcdYears = self.decToBcd(self, setYear)
        readReqBuf[0] = self.RTC_SECONDS_REG
        i2c.write(self.CHIP_ADDRESS, readReqBuf, False)
        readBuf = i2c.read(self.CHIP_ADDRESS, 1, False)
        readCurrentSeconds = readBuf[0]
        print(readCurrentSeconds)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.STOP_RTC
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_DAY_REG
        writeBuf[1] = bcdDay
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_MONTH_REG
        writeBuf[1] = bcdMonths
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_YEAR_REG
        writeBuf[1] = bcdYears
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.START_RTC | readCurrentSeconds
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        
rtc = KitronikRTC
rtc.setTime(rtc,6,4,20)
rtc.setDate(rtc, 5,11,55)
while True:
    display.scroll(rtc.readTimeAndDate(rtc))
