# 3. Стиль API та обробка помилок

* Статус: Прийнято
* Дата: 2025-11-28

## Рішення
* Використовуємо REST.
* Специфікація: OpenAPI 3.0.
* Формат помилок єдиний для всіх ендпоінтів:
```json
{
  "error": "ShortCode",
  "details": "Human readable description",
  "request_id": "uuid..."
}