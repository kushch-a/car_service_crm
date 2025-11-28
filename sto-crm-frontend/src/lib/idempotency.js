/**
 * Створює SHA-256 хеш для будь-якого об'єкта.
 * @param {unknown} obj - Об'єкт для хешування.
 * @returns {Promise<string>} - Шістнадцятковий рядок хешу.
 */
export async function payloadHash(obj) {
  const data = new TextEncoder().encode(JSON.stringify(obj));
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Отримує існуючий ключ ідемпотентності з localStorage або створює новий.
 * @param {unknown} payload - Пейлоад запиту.
 * @returns {Promise<string>} - Ключ ідемпотентності.
 */
export async function getOrReuseKey(payload) {
  const hash = await payloadHash(payload);
  const key = `idempotency:${hash}`;
  const existing = localStorage.getItem(key);
  
  if (existing) {
    return existing;
  }
  
  const freshKey = crypto.randomUUID();
  localStorage.setItem(key, freshKey);
  return freshKey;
}
