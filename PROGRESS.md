##  ML-сервис (24 сентября, вечер)

### Что сделано
- Модель сохранена в `models/model.pkl`
- FastAPI API с эндпоинтом `/predict`
- Swagger UI: http://localhost:8000/docs
- Протестирован: temperature=450, time=720 → angle=62.33°

### Команды
- Запуск: `py -m uvicorn app.main:app --reload`
- Тест: открыть http://localhost:8000/docs

### Следующее
- Dockerfile
- requirements.txt
- Деплой на VPS