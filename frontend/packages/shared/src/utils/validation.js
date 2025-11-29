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

export function validateEmail(value) {
  return isEmail(value);
}

export function validateName(value) {
  if (!required(value)) return 'Name is required';
  if (!minLength(value, 2)) return 'Name must be at least 2 characters';
  return '';
}

export function validatePassword(value) {
  if (!required(value)) return 'Password is required';
  if (!minLength(value, 8)) return 'Password must be at least 8 characters';
  const hasLetter = /[A-Za-z]/.test(String(value));
  const hasNumber = /\d/.test(String(value));
  if (!(hasLetter && hasNumber)) return 'Password must include letters and numbers';
  return '';
}
