# Qlik Sense Function Reference (Complete) — Datetime


> Split from `functions_reference.md`. Companion files share the `functions_` prefix.


## Date and Time Functions

### Key Date Format Variables (SET in script)

```qlik
SET DateFormat='DD/MM/YYYY';
SET TimeFormat='hh:mm:ss';
SET TimestampFormat='DD/MM/YYYY hh:mm:ss[.fff]';
SET FirstWeekDay=0;      // 0=Monday, 6=Sunday
SET BrokenWeeks=0;       // 0=ISO weeks, 1=non-ISO
SET ReferenceDay=4;      // minimum days in first ISO week
SET FirstMonthOfYear=1;  // fiscal year start month
```

### Date Extraction Functions

| Function | Syntax | Return | Example |
|----------|--------|--------|---------|
| `year` | `year(date)` | integer | `year('2024-06-15')` → `2024` |
| `month` | `month(date)` | dual (name + 1-12) | `month('2024-06-15')` → `Jun` |
| `day` | `day(date)` | integer | `day('2024-06-15')` → `15` |
| `hour` | `hour(timestamp)` | integer | `hour('09:14:36')` → `9` |
| `minute` | `minute(timestamp)` | integer | `minute('09:14:36')` → `14` |
| `second` | `second(timestamp)` | integer | `second('09:14:36')` → `36` |
| `week` | `week(date[, firstweekday[, brokenweeks]])` | integer | `week('2024-01-15')` → `3` |
| `weekday` | `weekday(date)` | integer 0-6 | `weekday('2024-06-15')` → `5` (Sat) |
| `weekyear` | `weekyear(date)` | integer | ISO week year |
| `quarter` | — | use `Ceil(Month(date)/3)` | |

### Date Construction Functions

#### makedate

```qlik
MakeDate(YYYY [, MM [, DD]])
// Returns dual date value
MakeDate(2024)         // 2024-01-01
MakeDate(2024, 6)      // 2024-06-01
MakeDate(2024, 6, 15)  // 2024-06-15
```

#### maketime

```qlik
MakeTime(hh [, mm [, ss]])
MakeTime(22)         // 22:00:00
MakeTime(22, 30)     // 22:30:00
MakeTime(22, 30, 45) // 22:30:45
```

#### makeweekdate

```qlik
MakeWeekDate(YYYY [, WW [, D]])
// D: 0=Monday ... 6=Sunday
MakeWeekDate(2024, 6)    // first day of week 6 of 2024
MakeWeekDate(2024, 6, 6) // Sunday of week 6 of 2024
```

### Period Boundary Functions

All functions below accept an optional `period_no` argument (negative = prior period, positive = future period).

#### Year boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `yearstart` | `YearStart(date [, period_no [, first_month_of_year]])` | First millisecond of year |
| `yearend` | `YearEnd(date [, period_no [, first_month_of_year]])` | Last millisecond of year |
| `yearname` | `YearName(date [, period_no [, first_month_of_year]])` | Display year string |

```qlik
YearStart('15/06/2024')        // returns 01/01/2024
YearEnd('15/06/2024')          // returns 31/12/2024 23:59:59
YearEnd('15/06/2024', -1)      // returns 31/12/2023 23:59:59
YearStart('15/06/2024', 0, 4)  // fiscal year starting April → 01/04/2024
```

#### Quarter boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `quarterstart` | `QuarterStart(date [, period_no [, first_month_of_year]])` | Start of quarter |
| `quarterend` | `QuarterEnd(date [, period_no [, first_month_of_year]])` | End of quarter |
| `quartername` | `QuarterName(date [, period_no [, first_month_of_year]])` | Display e.g. "Q2 2024" |

#### Month boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `monthstart` | `MonthStart(date [, period_no])` | First millisecond of month |
| `monthend` | `MonthEnd(date [, period_no])` | Last millisecond of month |
| `monthname` | `MonthName(date [, period_no])` | Display e.g. "Jun 2024" |

```qlik
MonthEnd('19/02/2024')      // 29/02/2024 23:59:59
MonthEnd('19/02/2024', -1)  // 31/01/2024 23:59:59
MonthEnd('19/02/2024', 4)   // 30/06/2024 23:59:59
```

#### Multi-month periods (bi-month, quarter, tertial, half-year)

```qlik
MonthsStart(n_months, date [, period_no [, first_month_of_year]])
MonthsEnd(n_months, date [, period_no [, first_month_of_year]])
MonthsName(n_months, date [, period_no [, first_month_of_year]])
```

`n_months` must be 1, 2, 3, 4, or 6.

```qlik
MonthsEnd(3, '15/06/2024')       // end of Q2 → 30/06/2024 23:59:59
MonthsEnd(6, '15/06/2024')       // end of H1 → 30/06/2024 23:59:59
MonthsName(3, '15/06/2024')      // 'Apr-Jun 2024'
MonthsName(4, '19/10/2024', -1)  // 'May-Aug 2024'
```

#### Week boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `weekstart` | `WeekStart(date [, period_no [, first_week_day]])` | First millisecond of week |
| `weekend` | `WeekEnd(date [, period_no [, first_week_day]])` | Last millisecond of week |
| `weekname` | `WeekName(date [, period_no [, first_week_day]])` | Display e.g. "2024/24" |

#### Day boundaries

| Function | Syntax | Returns |
|----------|--------|---------|
| `daystart` | `DayStart(timestamp [, period_no [, day_fraction]])` | Midnight start of day |
| `dayend` | `DayEnd(timestamp [, period_no [, day_fraction]])` | End of day |
| `dayname` | `DayName(timestamp [, period_no [, day_fraction]])` | Display date string |

#### Lunar week functions (Qlik proprietary — 7-day weeks from Jan 1)

| Function | Syntax |
|----------|--------|
| `lunarweekstart` | `LunarWeekStart(date [, period_no [, first_week_day]])` |
| `lunarweekend` | `LunarWeekEnd(date [, period_no [, first_week_day]])` |
| `lunarweekname` | `LunarWeekName(date [, period_no [, first_week_day]])` |

```qlik
LunarWeekEnd('12/01/2024')     // 14/01/2024 23:59:59
LunarWeekEnd('12/01/2024', -1) // 07/01/2024 23:59:59
```

### In-Period Functions

Return `-1` (True) or `0` (False).

| Function | Syntax | Checks |
|----------|--------|--------|
| `inyear` | `InYear(date, base_date, period_no [, first_month])` | Same year |
| `inyeartodate` | `InYearToDate(date, base_date, period_no [, first_month])` | Year-to-date |
| `inquarter` | `InQuarter(date, base_date, period_no [, first_month])` | Same quarter |
| `inquartertodate` | `InQuarterToDate(date, base_date, period_no [, first_month])` | QTD |
| `inmonth` | `InMonth(date, base_date, period_no)` | Same month |
| `inmonths` | `InMonths(n_months, date, base_date, period_no [, first_month])` | Same n-month period |
| `inmonthtodate` | `InMonthToDate(date, base_date, period_no)` | MTD |
| `inweek` | `InWeek(date, base_date, period_no [, first_week_day])` | Same ISO week |
| `inweektodate` | `InWeekToDate(date, base_date, period_no [, first_week_day])` | Week-to-date |
| `inday` | `InDay(timestamp, base_timestamp, period_no [, day_start])` | Same day |
| `indaytotime` | `InDayToTime(timestamp, base_timestamp, period_no [, day_start])` | Day-to-time |
| `inlunarweek` | `InLunarWeek(date, base_date, period_no [, first_week_day])` | Same lunar week |
| `inlunarweektodate` | `InLunarWeekToDate(date, base_date, period_no [, first_week_day])` | Lunar WTD |

```qlik
// Load only records from current year
LOAD * FROM data.csv WHERE InYear(TransDate, Today(), 0);

// YTD sales (in chart)
Sum({$<Date = {"=InYearToDate(Date, Today(), 0)"}>} Sales)
```

### Date Arithmetic Functions

#### addmonths

```qlik
AddMonths(startdate, n [, mode])
// Adds n months; mode=0 (default) end-of-month-aware
AddMonths('31/01/2024', 1)   // 29/02/2024
AddMonths('31/01/2024', -1)  // 31/12/2023
```

#### addyears

```qlik
AddYears(startdate, n)
AddYears('28/02/2024', 1)  // 28/02/2025
```

#### networkdays

```qlik
NetworkDays(start_date, end_date [, holiday])
// Returns working days between dates (Mon-Fri), excluding holidays
NetworkDays('01/06/2024', '30/06/2024')
NetworkDays('01/06/2024', '30/06/2024', '10/06/2024')
```

#### age

```qlik
Age(timestamp, date_of_birth)
// Returns completed years of age
Age(Today(), '15/06/1990')
```

#### daystart / dayend

```qlik
DayStart('2024-06-15 14:30:00')  // 2024-06-15 00:00:00
DayEnd('2024-06-15 14:30:00')    // 2024-06-15 23:59:59
```

#### firstworkdate / lastworkdate

```qlik
FirstWorkDate(end_date, no_of_workdays [, holiday])
LastWorkDate(start_date, no_of_workdays [, holiday])
```

#### setdateyear / setdateyearmonth

```qlik
SetDateYear(date, year)       // replace year in date
SetDateYearMonth(date, year, month) // replace year and month
```

#### now / today / GMT / UTC / localtime

```qlik
Now([timer_mode])      // current timestamp, timer_mode: 0=reload time, 1=current
Today([timer_mode])    // current date
GMT()                  // Greenwich Mean Time
UTC()                  // UTC timestamp
LocalTime([timezone [, ignoreDST]])
```

#### DayLightSaving

```qlik
DayLightSaving()   // returns True if daylight saving is active
```

#### timezone

```qlik
TimeZone()   // returns name of local timezone
```

#### converttolocaltime

```qlik
ConvertToLocalTime(timestamp [, place [, ignore_dst]])
```

#### daynumberofquarter / daynumberofyear

```qlik
DayNumberOfQuarter(date [, first_month_of_year])
DayNumberOfYear(date [, first_month_of_year])
```

---
