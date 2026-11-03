// RESTX accepts omitted optional numbers, but not JSON null.
export function normalizeEventPayload(data) {
  const numbers = ['latitude', 'longitude', 'distance_to_center', 'time_to_nearest_stop']
  return Object.fromEntries(Object.entries(data).flatMap(([key, value]) => {
    if (numbers.includes(key)) return value == null || value === '' ? [] : [[key, Number(value)]]
    return [[key, value ?? '']]
  }))
}

export function sessionPayload(session) {
  return {
    start_datetime: session.start_datetime?.replace(' ', 'T'),
    max_participants: session.max_participants,
    cost: Number(session.cost),
  }
}
