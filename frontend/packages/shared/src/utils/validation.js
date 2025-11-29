export function required(value) {
  return value !== undefined && value !== null && String(value).trim().length > 0;
}

export function minLength(value, length) {
  return String(value || "").length >= Number(length || 0);
}

export function isEmail(value) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(value || "").toLowerCase());
}

export function equals(a, b) {
  return String(a) === String(b);
}
