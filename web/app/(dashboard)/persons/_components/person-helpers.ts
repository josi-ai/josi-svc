/** Format time for API: "HH:MM" -> "HH:MM:SS" */
export function formatTimeForApi(
  time: string | null,
  _dob?: string | null,
): string | null {
  if (!time) return null;
  // Backend expects just the time portion: HH:MM, HH:MM:SS, or HH:MM AM/PM
  return time.length === 5 ? `${time}:00` : time;
}

export function formatDateOfBirth(dateStr: unknown): string | null {
  if (!dateStr || typeof dateStr !== 'string') return null;
  const [year, month, day] = dateStr.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatTimeOfBirth(timeStr: string | null): string | null {
  if (!timeStr) return null;
  // timeStr may be "HH:MM", "HH:MM:SS", or a full datetime string
  // Try to extract hours and minutes
  let hours: number;
  let minutes: number;
  if (timeStr.includes('T')) {
    // ISO datetime string
    const d = new Date(timeStr);
    hours = d.getHours();
    minutes = d.getMinutes();
  } else {
    const parts = timeStr.split(':');
    hours = parseInt(parts[0], 10);
    minutes = parseInt(parts[1], 10);
  }
  if (isNaN(hours) || isNaN(minutes)) return timeStr;
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const h = hours % 12 || 12;
  const m = minutes.toString().padStart(2, '0');
  return `${h}:${m} ${ampm}`;
}

/** Extract HH:MM from various time formats for form input */
export function extractTimeValue(timeOfBirth: string | null): string {
  if (!timeOfBirth) return '';
  const t = timeOfBirth;
  if (t.includes('T')) {
    // ISO datetime — extract time portion
    const d = new Date(t);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  }
  // Already HH:MM or HH:MM:SS
  return t.substring(0, 5);
}
