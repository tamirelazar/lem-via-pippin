/**********************************************
 * chart-utils.js
 * Helper functions for chart/time-range logic
 **********************************************/

// getPeriodKey returns a "bucket" based on the timeRange
function getPeriodKey(date, timeRange) {
  switch(timeRange) {
    case 'hourly':
      return `${date.getFullYear()}-${padNumber(date.getMonth()+1)}-${padNumber(date.getDate())}-${padNumber(date.getHours())}`;
    case 'daily':
      return `${date.getFullYear()}-${padNumber(date.getMonth()+1)}-${padNumber(date.getDate())}`;
    case 'weekly': {
      const weekNumber = getWeekNumber(date);
      return `${date.getFullYear()}-W${padNumber(weekNumber)}`;
    }
    case 'monthly':
      return `${date.getFullYear()}-${padNumber(date.getMonth()+1)}`;
    default:
      return `${date.getFullYear()}-${padNumber(date.getMonth()+1)}-${padNumber(date.getDate())}`;
  }
}

// getPeriodDate reconstructs a Date from a "periodKey"
function getPeriodDate(periodKey, timeRange) {
  const parts = periodKey.split('-');
  switch(timeRange) {
    case 'hourly':
      return new Date(parts[0], parts[1]-1, parts[2], parts[3]);
    case 'daily':
      return new Date(parts[0], parts[1]-1, parts[2]);
    case 'weekly': {
      const [year, week] = parts[1].split('W');
      return getDateOfWeek(parseInt(week,10), parseInt(year,10));
    }
    case 'monthly':
      return new Date(parts[0], parts[1]-1, 1);
    default:
      return new Date(parts[0], parts[1]-1, parts[2] || 1);
  }
}

// getAllPeriods returns a sorted array of all "period" keys from start -> end
function getAllPeriods(start, end, timeRange) {
  const periods = [];
  const current = new Date(start);
  while (current <= end) {
    periods.push(getPeriodKey(current, timeRange));
    switch(timeRange) {
      case 'hourly':
        current.setHours(current.getHours()+1);
        break;
      case 'daily':
        current.setDate(current.getDate()+1);
        break;
      case 'weekly':
        current.setDate(current.getDate()+7);
        break;
      case 'monthly':
        current.setMonth(current.getMonth()+1);
        break;
      default:
        current.setDate(current.getDate()+1);
    }
  }
  return periods;
}

// Utility: pad a number to 2 digits
function padNumber(num) {
  return String(num).padStart(2,'0');
}

// getWeekNumber returns ISO week number
function getWeekNumber(d) {
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay()||7));
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(),0,1));
  return Math.ceil(((date - yearStart)/86400000 +1)/7);
}

// getDateOfWeek returns date for the "year-weekNumber" at Monday
function getDateOfWeek(weekNumber, year) {
  const simple = new Date(year, 0, 1 + (weekNumber-1)*7);
  const dow = simple.getDay();
  const ISOweekStart = new Date(simple);
  if (dow <= 4) {
    ISOweekStart.setDate(simple.getDate() - simple.getDay()+1);
  } else {
    ISOweekStart.setDate(simple.getDate() +8 - simple.getDay());
  }
  return ISOweekStart;
}
