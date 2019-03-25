# перед тестированием нужно запустить сервер (index.py)
from requests import get, post, delete
# Получение списка всех новостей
print(get('http://localhost:8080/api/news').json())
# Получение одной новости по id
print(get('http://localhost:8080/api/news/1').json())
print(get('http://localhost:8080/api/news/8').json())
# Добавление новости
print(post('http://localhost:8080/api/news').json())
print(post('http://localhost:8080/api/news', json={'title': 'Заголовок'}).json())
print(post('http://localhost:8080/api/news', json={'title': 'Заголовок', 'content': 'Текст новости', 'user_id': 1}).json())
# Удаление новости

print(delete('http://localhost:8080/api/news/2').json())
print(delete('http://localhost:8080/api/news/3').json())