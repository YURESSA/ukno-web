# Ошибки API: маршруты, статусы и тексты

Справочник для `main-backend`. Тексты приведены в исходном языке: русский и английский
не унифицировались, чтобы сохранить совместимость. Файл описывает текущее поведение,
а не вводит новые машинные коды или новые ответы.

## Формат и правила чтения

```json
{"message": "Недостаточно свободных мест"}
```

В ошибочном ответе Flask поле `message` — непустая строка. Дополнительные поля
`msg`, `errors`, `available`, `max_content_length`, `max_form_memory_size`, `data`
сохраняются. HTTP-статус определяет тип ошибки; проверять текст как постоянный код
ошибки не следует. Порядок проверок важен: сервер возвращает первую обнаруженную ошибку.

В таблицах `{id}`, `{email}` и другие параметры URL заменяются фактическими значениями.
`{str(e)}`, `{field}`, `{missing}` и аналогичные вставки в сообщениях — переменные части,
а не буквальный текст. Например, шаблон `Ошибка при добавлении фото: {str(e)}` может
вернуть `Ошибка при добавлении фото: Storage timeout`. Тексты исключений Python,
SQLAlchemy, хранилища и платёжного SDK заранее полностью перечислить нельзя.

Маршруты в одной ячейке разделены `<br>`. Для всех операций действуют общие ошибки
ниже. Если специальная ошибка здесь не указана, непредвиденное исключение обрабатывается
общим ответом 500. Успешные ответы 2xx в справочник не включены.

## Общие ошибки HTTP, JSON и форм

| Где / когда | HTTP | `message` и дополнительные поля |
|---|---|---|
| Непредвиденное исключение в обработчике | 500 | `Internal server error`; подробности записываются в лог |
| JSON-массив, строка, число, boolean или null вместо объекта в теле POST/PUT/PATCH/DELETE | 400 | `JSON должен содержать объект` |
| Такое же значение в JSON-поле `data` новости или экскурсии | 400 | `JSON должен содержать объект` |
| Синтаксически неверный JSON HTTP-тела | 400 | Сообщение Werkzeug; в обычном режиме `The browser (or proxy) sent a request that this server could not understand.`; debug может дополнять его деталями декодирования |
| Чтение JSON при неподходящем Content-Type | 415 | `Did not attempt to load JSON data because the request Content-Type was not 'application/json'.` |
| Неизвестный URL | 404 | `The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.` |
| HTTP-метод не поддерживается маршрутом | 405 | `The method is not allowed for the requested URL.`; допустимые методы — в заголовке `Allow` |
| Превышены лимиты тела запроса / формы / multipart | 413 | `Uploaded form data is too large`; дополнительно `max_content_length`, `max_form_memory_size` |
| Не прошла проверка модели Swagger или reqparse | 400 | `Input payload validation failed`; в `errors` находятся имена полей и пояснения |
| Пример отсутствующего поля формы `full_name` | 400 | `message`: `Input payload validation failed`; `errors.full_name`: `Missing required parameter in the post body` |
| Искусственно сформирован ответ без сообщения | Исходный статус | Берётся прежнее `msg`, `error` или `detail`; иначе английское название HTTP-статуса, например `Bad Request`, `Conflict`, `Too Many Requests`; для неизвестного статуса — `Request failed` |

Текст `errors.<поле>` зависит от модели, типа значения, параметра `help` и версии
Flask-RESTX/jsonschema. Например, обязательное поле JSON может дать
`'email' is a required property`, а поле неверного типа — `123 is not of type 'string'`.
Это примеры, не закрытый список. Точный `errors` нужно показывать/разбирать как данные
ответа. Заголовок `Content-Type` всех этих JSON-ответов — `application/json`.

HEAD по HTTP не передаёт тело. Ошибки nginx, прокси и сетевые обрывы не проходят через
обработчик Flask и не обязаны содержать JSON. Например, лимит запросов nginx может
сам вернуть 429; это отдельная конфигурация развёртывания.

## JWT и права доступа

Применяется к методам с `jwt_required`, `admin_required` или `resident_required`.
У JWT-ошибок сохранено `msg`, а `message` содержит тот же текст.

| Когда | HTTP | Текст `message` / шаблон |
|---|---|---|
| Отсутствует Authorization | 401 | `Missing Authorization Header` |
| Истёк срок действия | 401 | `Token has expired` |
| Отозван токен при настроенной проверке blocklist | 401 | `Token has been revoked` |
| Маршрут требует fresh-токен | 401 | `Fresh token required` — только если такой режим используется |
| JWT не имеет трёх частей | 422 | `Not enough segments` |
| Неверная подпись | 422 | `Signature verification failed` |
| Refresh-токен передан вместо access-токена | 422 | `Only non-refresh tokens are allowed` |
| Заголовок без правильного типа Bearer | 401 | `Missing 'Bearer' type in 'Authorization' header. Expected 'Authorization: Bearer <JWT>'` |
| У Bearer-заголовка неверное количество частей | 422 | `Bad Authorization header. Expected 'Authorization: Bearer <JWT>'` |
| Не удалось декодировать заголовок / payload / claims | 422 | Текст исключения JWT; например `Invalid header padding`, `Subject must be a string` |
| Администратор не найден, понижен в роли или роль JWT не совпадает | 403 | `Доступ запрещен` — буква «е» |
| Резидент не найден, понижен в роли или роль JWT не совпадает | 403 | `Доступ запрещён` — буква «ё» |

Строки JWT поступают из Flask-JWT-Extended/PyJWT; переменные части зависят от
повреждения токена. Проверки fresh/blocklist здесь описаны как возможности библиотеки:
не все они включены в текущих маршрутах. При ошибке авторизации бизнес-логика не исполняется.

## Вход, регистрация и профиль

| Метод и маршрут | Когда | HTTP | Точный `message` / шаблон |
|---|---|---|---|
| `POST /api/login` | Нет email или пароля | 400 | `Необходимо указать email и пароль` |
| `POST /api/user/login`<br>`POST /api/admin/login`<br>`POST /api/resident/login` | Нет email или пароля | 400 | `Необходимо указать и email, и пароль` |
| Все четыре маршрута входа | Email не найден либо пароль неверный | 401 | `Неверный email или пароль` |
| Вход пользователя/администратора/резидента через ролевой маршрут | У аккаунта другая роль | 403 | `Доступ запрещён для этой роли` |
| Все маршруты входа | Генератор не вернул JWT | 500 | `Ошибка при генерации токена` |
| `POST /api/user/register`<br>`POST /api/admin/users` | Нет email, пароля или полного имени | 400 | `Необходимо указать email, пароль и полное имя` |
| Те же маршруты | Телефон длиннее 32 символов | 400 | `Номер телефона не должен превышать 32 символа` |
| Те же маршруты | Пользователь уже существует | 409 | `Пользователь с таким именем или почтой уже существует либо роль недопустима` |
| `GET /api/user/profile`<br>`GET /api/resident/profile`<br>`GET /api/admin/profile` | Пользователь не найден, если запрос прошёл проверку роли/JWT | 404 | `Пользователь не найден` |
| `PUT /api/user/profile` | Новый email занят | 400 | `Этот email уже используется` |
| `PUT /api/user/profile` | Текущий пользователь не найден | 404 | `Пользователь не найден` |
| `PUT /api/admin/users/detail/{email}` | Пустой JSON-объект | 400 | `Пустой JSON` |
| `GET/PUT/DELETE /api/admin/users/detail/{email}` | Целевой пользователь не найден | 404 | `Пользователь не найден` |
| `PUT /api/admin/users/detail/{email}` | Новый email занят | 400 | `Email уже используется другим пользователем` |
| Тот же метод | Недопустимая роль | 400 | `Роль '{role_name}' не найдена. Допустимые значения: admin, resident, user` |
| `DELETE /api/user/profile`<br>`DELETE /api/resident/profile`<br>`DELETE /api/admin/users/detail/{email}` | Есть созданные экскурсии | 400 | `Невозможно удалить пользователя: у него есть {created_events} созданных экскурсий` |
| Те же методы | Есть активные бронирования | 400 | `Невозможно удалить пользователя: у него есть {active_reservations} активных бронирований` |
| Те же методы | Пользователь не найден, если запрос прошёл авторизацию | 404 | `Пользователь не найден` |
| `PUT /api/user/profile/password`<br>`PUT /api/resident/profile` | Нет старого или нового пароля | 400 | `Оба поля обязательны` |
| Те же методы | Старый пароль неверный | 401 | `Неверный текущий пароль` |
| Те же методы | Пользователь не найден | 404 | `Пользователь не найден` |
| `PUT /api/admin/profile` | Нет старого или нового пароля | 400 | `Старый и новый пароль обязательны` |
| Тот же метод | Старый пароль неверный | 400 | `Неверный старый пароль` |
| `POST /api/user/password-reset` | Токен неверный или просрочен | 400 | `Неверный или просроченный токен` |
| Тот же метод | Пользователь из токена не найден | 404 | `Пользователь не найден` |

`POST /api/user/password-reset-request` намеренно не выдаёт ошибку, если email не найден:
это защищает от перебора существующих аккаунтов. Ошибки формы и непредвиденные сбои
обрабатываются по общим правилам.

## Бронирования и платежи

| Метод и маршрут | Когда | HTTP | Точный `message` / шаблон |
|---|---|---|---|
| `GET /api/user/reservations`<br>`POST/DELETE /api/user/v2/reservations` | Пользователь из JWT отсутствует | 401 | `Пользователь не найден` |
| `POST /api/user/v2/reservations` | Нет session_id | 400 | `session_id is required` |
| Тот же метод | Число участников не положительное целое | 400 | `Количество участников должно быть положительным целым числом` |
| Тот же метод | Сеанс отсутствует | 404 | `Сеанс не найден` |
| Тот же метод | Событие отсутствует или неактивно | 400 | `Событие недоступно для бронирования` |
| Тот же метод | Сеанс уже начался | 400 | `Нельзя забронировать прошедший сеанс` |
| Тот же метод | Уже есть активная бронь | 409 | `У вас уже есть активное бронирование на этот сеанс` |
| Тот же метод | Недостаточно мест | 409 | `Недостаточно свободных мест` |
| Тот же метод | Провайдер не создал платёж | 502 | `Не удалось создать платёж` |
| `DELETE /api/user/v2/reservations` | Нет reservation_id | 400 | `reservation_id is required` |
| Тот же метод | Бронь не найдена или принадлежит другому пользователю | 404 | `Бронирование не найдено или не принадлежит вам` |
| Тот же метод | Бронь уже отменена | 400 | `Бронирование уже отменено` |
| Тот же метод | Сбой возврата средств | 500 | `Не удалось сделать возврат средств` |
| `GET /api/user/reservations/{reservation_id}/export_ical`<br>`GET /api/user/reservations/{reservation_id}/google_calendar_link` | Бронь не найдена или чужая | 404 | `Бронирование не найдено` |
| `GET/DELETE /api/admin/reservations/{reservation_id}` | Бронь отсутствует | 404 | `Бронь не найдена` |
| `DELETE /api/admin/reservations/{reservation_id}` | Возврат получил неуспешный статус | 400 | `Не удалось вернуть средства, статус возврата: {refund.status}` |
| Тот же метод | Исключение при возврате | 500 | `Ошибка при попытке возврата средств: {str(e)}` |
| Тот же метод | Исключение при удалении записи | 500 | `Ошибка при удалении брони: {str(e)}` |

## Экскурсии, сеансы и фото

`{scope}` ниже — `admin` или `resident`. Для резидента дополнительно проверяется
владение объектом: `403` с текстом `У вас нет доступа к этой экскурсии`.

| Метод и маршрут | Когда | HTTP | Точный `message` / шаблон |
|---|---|---|---|
| `GET /api/user/excursions_detail/{excursion_id}`<br>`GET/PATCH/DELETE /api/{scope}/excursions/{excursion_id}` | Экскурсия отсутствует | 404 | `Экскурсия не найдена` |
| `POST /api/{scope}/excursions` | Нет поля формы data | 400 | `Поле 'data' обязательно` |
| Тот же метод | Некорректный JSON в data | 400 | `Неверный JSON: {str(e)}` |
| Тот же метод | Категория, формат или возрастная категория не найдены | 400 | `Категория не найдена` / `Формат мероприятия не найден` / `Возрастная категория не найдена` |
| Тот же метод | Нет места проведения | 400 | `Место проведения обязательно` |
| `PATCH /api/{scope}/excursions/{excursion_id}` | Справочник с указанным именем отсутствует | 400 | `Категория '{data['category']}' не найдена` / `Формат '{data['format_type']}' не найден` / `Возрастная категория '{data['age_category']}' не найдена` |
| `POST /api/{scope}/excursions/{excursion_id}/sessions` | Дата отсутствует или не распознаётся | 400 | `Неверный или отсутствует start_datetime` |
| `PATCH /api/{scope}/excursions/{excursion_id}/sessions/{session_id}` | Неверная дата | 400 | `Неверный формат start_datetime` |
| `PATCH/DELETE /api/{scope}/excursions/{excursion_id}/sessions/{session_id}` | Сеанс отсутствует | 404 | `Сессия не найдена` |
| `DELETE /api/{scope}/excursions/{excursion_id}/sessions/{session_id}` | Возврат по брони вызвал исключение | 400 | `Ошибка возврата по брони {res.reservation_id}: {str(e)}` |
| `POST /api/{scope}/excursions/{excursion_id}/photos` | Нет файла photo | 400 | `Фото не загружено` |
| Тот же метод | Файл был пропущен при обработке | 400 | `Недопустимый файл` |
| `GET /api/{scope}/excursions/{excursion_id}/photos` | Экскурсия не найдена | 404 | `Экскурсия не найдена` |
| `DELETE /api/{scope}/excursions/{excursion_id}/photos/{photo_id}` | Фото не связано с экскурсией или отсутствует | 404 | `Фото не найдено` |

Ошибки создания/обновления/удаления экскурсии и сеанса могут возвращать 500 с
шаблонами `Ошибка при создании экскурсии: {str(e)}`, `Ошибка при обновлении экскурсии: {str(e)}`,
`Ошибка при удалении экскурсии: {str(e)}`, `Ошибка при создании сессии: {str(e)}`,
`Ошибка при обновлении сессии: {str(e)}`, `Ошибка при удалении сессии: {str(e)}`.
При сбое фото: `Ошибка при сохранении фото: {str(e)}` или `Ошибка при удалении фото: {str(e)}`.
При каскадном удалении экскурсии ошибка дочерней сессии передаёт её статус и текст
`Ошибка при удалении сессии ID {session.session_id}: {result.get('message', '')}`.

## Новости

| Метод и маршрут | Когда | HTTP | Точный `message` / шаблон |
|---|---|---|---|
| `GET /api/user/news/{news_id}`<br>`GET/PUT/DELETE /api/admin/news/{news_id}`<br>`GET/POST /api/admin/news/{news_id}/photos` | Новости нет | 404 | `Новость не найдена` |
| `POST /api/admin/news`<br>`PUT /api/admin/news/{news_id}` | Нет data | 400 | `Поле 'data' обязательно` — reqparse также может вернуть общую ошибку формы |
| Те же методы | JSON поля data синтаксически неверен | 400 | `Ошибка в JSON: {str(e)}` |
| Те же методы | Неверная created_at | 400 | `Неверный формат даты` |
| `POST /api/admin/news` | Нет title или content | 400 | `Поля title и content обязательны` |
| Тот же метод | Автор отсутствует | 404 | `Пользователь не найден` |
| `POST /api/admin/news/{news_id}/photos` | Нет файла photo | 400 | `Фото не загружено` |
| Тот же метод | Сбой сохранения, в том числе исключение валидации изображения | 500 | `Ошибка при добавлении фото: {str(e)}` |
| `DELETE /api/admin/news/{news_id}/photos/{photo_id}` | Фото отсутствует | 404 | `Фото не найдено` |
| Тот же метод | Сбой удаления | 500 | `Ошибка при удалении фото: {str(e)}` |

При создании новости и добавлении изображений через PUT типизированные ошибки
проверки файла могут возвращаться как 400; отдельный POST `/photos` сохраняет своё
историческое поведение 500 с префиксом сообщения, описанным выше.

## Справочники и файлы

Все пути в этой секции начинаются с `/api/references`. POST/PUT/DELETE требуют администратора.
GET-списки возвращают пустой список при отсутствии записей, а не 404.

| Маршрут / действие | Когда | HTTP | Точный `message` |
|---|---|---|---|
| POST `/categories` | Нет name / имя занято | 400 | `Поле name обязательно` / `Категория с таким именем уже существует` |
| DELETE `/categories/{id}` | Записи нет | 404 | `Категория не найдена` |
| POST `/age-categories` | Нет name / имя занято | 400 | `Поле name обязательно` / `Возрастная категория с таким именем уже существует` |
| DELETE `/age-categories/{id}` | Записи нет | 404 | `Возрастная категория не найдена` |
| POST `/format-types` | Нет name / имя занято | 400 | `Поле name обязательно` / `Тип формата с таким именем уже существует` |
| DELETE `/format-types/{id}` | Записи нет | 404 | `Тип формата не найден` |
| POST `/projects`, PUT `/projects/{id}` | Нет title / link | 400 | `Поле title обязательно` / `Поле link обязательно` |
| GET/PUT/DELETE `/projects/{id}` | Записи нет | 404 | `Проект не найден` |
| POST `/history`, PUT `/history/{id}` | Нет title / date / description | 400 | `Поле title обязательно` / `Поле date обязательно` / `Поле description обязательно` |
| Те же методы | Дата не распознаётся | 400 | `Неверный формат даты. Используйте YYYY-MM-DD` |
| GET/PUT/DELETE `/history/{id}` | Записи нет | 404 | `Событие не найдено` |
| POST `/trust-reasons` | Нет title | 400 | `Поле title обязательно` |
| DELETE `/trust-reasons/{id}` | Записи нет | 404 | `Причина не найдена` |
| POST `/partners`, PUT `/partners/{id}` | Нет name | 400 | `Поле name обязательно` |
| GET/PUT/DELETE `/partners/{id}`, POST/DELETE `/partners/{id}/photo` | Партнёра нет | 404 | `Партнёр не найден` |
| POST `/cultural-space`, PUT `/cultural-space/{id}` | Нет text | 400 | `Поле text обязательно` |
| GET/PUT/DELETE `/cultural-space/{id}`, POST/DELETE `/cultural-space/{id}/photo` | Элемента нет | 404 | `Элемент не найден` |
| POST `/team`, PUT `/team/{id}` | Нет full_name | 400 | `Поле full_name обязательно` |
| GET/PUT/DELETE `/team/{id}`, POST/DELETE `/team/{id}/photo` | Сотрудника нет | 404 | `Сотрудник не найден` |
| DELETE `/{partners,cultural-space,team}/{id}/photo` | У записи нет фотографии | 400 | `Фото отсутствует` |
| POST `/requisites`, PUT `/requisites/{id}` | Нет title | 400 | `Название обязательно` |
| POST `/requisites` | Нет file | 400 | `Файл обязателен` |
| GET/PUT/DELETE `/requisites/{id}`, POST/DELETE `/requisites/{id}/file` | Реквизита нет | 404 | `Реквизит не найден` |
| DELETE `/requisites/{id}/file` | Нет файла | 400 | `Файл отсутствует` |
| Загрузка/замена файла или фото, когда сервис получает пустой файл | Сервис не получил файл | 400 | `Файл не выбран`; reqparse может раньше вернуть ошибку обязательного поля |

### Проверки изображения

| Когда | Точный `message` |
|---|---|
| Content-Type не начинается с image/ | `Файл должен быть изображением` |
| Предварительная проверка обнаружила размер больше 5 MiB | `Размер файла не должен превышать 5 MB` |
| Расширение отсутствует, запрещено настройками или не поддерживается | `Недопустимый формат изображения` |
| Проверка содержимого: пустой файл или размер больше 5 MiB | `Размер изображения должен быть от 1 байта до 5 МБ` |
| Сигнатура не соответствует расширению | `Содержимое файла не соответствует формату изображения` |

Эти сообщения обычно имеют статус 400. Исключения текущего контракта:

- POST `/api/references/cultural-space/{id}/photo`: ошибка валидации фото имеет **404** с тем же текстом.
- POST `/api/admin/news/{news_id}/photos`: ошибка сохранения имеет **500** и префикс `Ошибка при добавлении фото: `.
- Ошибка файловой системы/S3, не являющаяся ошибкой валидации: общий 500 либо специальный 500 обработчика фото.

## Мерч

Существующие английские тексты не переводились. `{product_id}`, `{color_id}`,
`{cart_item_id}` и `{order_id}` в маршрутах — параметры URL.

| Метод и маршрут | Когда | HTTP | Точный `message` / шаблон |
|---|---|---|---|
| POST `/api/admin/merch/banners` | Нет image_path и файла image | 400 | `image_path or image is required` |
| PUT/DELETE `/api/admin/merch/banners/{banner_id}` | Баннера нет | 404 | `Banner not found` |
| POST `/api/admin/merch/categories`, PUT `/api/admin/merch/categories/{category_id}` | Нет name | 400 | `name is required` |
| Те же методы | Конфликт имени/slug | 400 | `Category name or slug already exists` |
| PUT/DELETE `/api/admin/merch/categories/{category_id}` | Категории нет | 404 | `Category not found` |
| DELETE `/api/admin/merch/categories/{category_id}` | Есть товары | 400 | `Category has products` |
| POST `/api/admin/merch/products` | Нет category_id, name или price | 400 | `Missing fields: {', '.join(missing)}`; пример `Missing fields: category_id, name, price` |
| POST `/api/admin/merch/products`, PUT `/api/admin/merch/products/{product_id}` | Категории нет | 404 | `Category not found` |
| Те же методы | Конфликт записей БД | 400 | `Product data conflicts with existing records` |
| GET/PUT/DELETE `/api/admin/merch/products/{product_id}`<br>GET `/api/user/merch/products/{product_id}`<br>POST `/api/user/merch/products/{product_id}/favorite` | Товар отсутствует/удалён | 404 | `Product not found` |
| Операции colors, sizes, images товара | Товара нет | 404 | `Product not found` |
| POST `/api/admin/merch/products/{product_id}/colors` | Нет имени цвета | 400 | `Color name is required` |
| Тот же метод | Конфликт цвета/размера | 400 | `Product color or size conflicts with existing records` |
| POST `/api/admin/merch/products/{product_id}/colors/{color_id}/sizes` | Цвета нет / он от другого товара | 404 | `Color not found` |
| Тот же метод | Конфликт размера | 400 | `Product size conflicts with existing records` |
| Создание/обновление товара, цвета и размеров | Вариант принадлежит другому товару/цвету | 400 | `Variant belongs to another product` / `Variant belongs to another color` |
| Те же действия | Нет корректного цвета или размера | 400 | `Valid color_id is required for variant` / `Valid color is required for color sizes` / `Valid size_id is required for each variant` / `size_name is required for each variant` |
| POST `/api/admin/merch/products/{product_id}/images` | Нет изображений | 400 | `At least one image is required` |
| PUT/DELETE `/api/admin/merch/products/{product_id}/images/{image_id}` | Изображение отсутствует/чужое/товар удалён | 404 | `Image not found` |
| POST/PUT мерча с JSON в поле data | Синтаксически неверные данные | 400 | `Invalid JSON payload` |
| Те же методы | Декодировалось не в объект | 400 | `JSON payload must be an object` |
| Защищённые операции корзины/заказов/избранного | Пользователь из JWT отсутствует | 401 | `User not found` |
| POST `/api/user/merch/cart`, PUT `/api/user/merch/cart/{cart_item_id}` | Вариант недоступен | 404 | `Variant not found` |
| Те же методы | Количество меньше единицы | 400 | `quantity must be greater than zero` |
| Те же методы | Недостаточный остаток | 400 | `Not enough stock`; дополнительно `available` |
| PUT/DELETE `/api/user/merch/cart/{cart_item_id}` | Позиции нет или она чужая | 404 | `Cart item not found` |
| POST `/api/user/merch/orders` | Нет last_name, first_name или contact_channel | 400 | `{field} is required`; пример `last_name is required` |
| Тот же метод | Способ доставки не pickup | 400 | `Only pickup delivery is supported` |
| Тот же метод | Нет pay_by_card | 400 | `pay_by_card is required` |
| Тот же метод | Корзина пуста | 400 | `Cart is empty` |
| Тот же метод | Товар или вариант стали недоступны | 400 | `Cart contains unavailable products` |
| Тот же метод | Недостаточный остаток при оформлении | 400 | `Not enough stock`; дополнительно `available`, `variant_id` |
| Тот же метод | Не удалось создать платёж | 502 | `Failed to create payment` |
| PUT/PATCH `/api/admin/merch/orders/{order_id}` | Заказа нет | 404 | `Order not found` |

Ошибки преобразования чисел в мерче иногда возвращаются как `str(exc)` с 400.
Их конкретный текст задаётся Python/decimal, а не постоянной строкой приложения.

## Webhook и Яндекс

| Метод и маршрут | Когда | HTTP | Точный `message` / шаблон |
|---|---|---|---|
| POST `/api/webhook/yookassa` | Нет данных, неверный type или нет event | 400 | `Invalid webhook payload` |
| Тот же метод | Нет object.id для платежа | 400 | `Missing payment id` |
| Тот же метод | Провайдер не подтвердил платежный статус/id | 400 | `Payment status verification failed` |
| Тот же метод | Нет object.id для возврата | 400 | `Missing refund id` |
| Тот же метод | Провайдер не подтвердил возврат | 400 | `Refund status verification failed` |
| Тот же метод | Не удалось запросить платёж у провайдера | 503 | `Could not verify payment` |
| Тот же метод | Не удалось запросить возврат у провайдера | 503 | `Could not verify refund` |
| GET `/api/yandex/map-helper` | Нет suggest | 400 | `Необходим параметр suggest` |
| Тот же метод | Исключение внешнего сервиса | 500 | `Ошибка сервиса Яндекса: {str(e)}` |

## Поддержание актуальности

Источники поведения — обработчики в `backend/api`, сервисы в `backend/core/services`,
общие проверки в `backend/core/utilits` и обработчики Flask в `backend/core/__init__.py`.
Swagger описывает схемы и статусы; этот файл дополнительно фиксирует точные тексты.

После изменения сообщения, статуса или проверки:

1. Сверить и при необходимости обновить таблицы маршрутов выше и Swagger.
2. Выполнить `python backend/core/scripts/generate_error_docs.py` — обновится только автоматически сформированный раздел ниже.
3. Выполнить `python backend/core/scripts/generate_error_docs.py --check` или `python -m pytest tests/test_error_documentation.py`.

Проверка замечает изменения извлекаемых строк, шаблонов, статусов и условий в исходниках.
Она не доказывает достижимость каждой ветки и не обновляет вручную написанные таблицы
маршрутов: их точность проверяется отдельно при изменении вызывающего обработчика.
Сообщения сторонних библиотек и динамические `str(exc)` требуют проверки HTTP-тестами.

<!-- BEGIN GENERATED ERROR CATALOG -->

## Каталог сообщений из исходников

Раздел обновляется автоматически; вручную редактируются таблицы маршрутов выше.

Статусы без звёздочки взяты из явных возвратов. `400*` и `404*` — стандартный статус
типизированного исключения, который вызывающий обработчик может переопределить.
`исключение` и `вызывающий код` требуют сверки с таблицами маршрутов выше.
В частности, загрузка фото культурного пространства возвращает 404, а обработчик фото
новостей преобразует исключение сохранения в 500. Условия в последней колонке —
фрагменты Python из исходного кода, а не отдельные проверки всех входных данных.

### [backend/api/admin/admin_auth.py](../api/admin/admin_auth.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `put` | `400` | `Неверный старый пароль` | `Ветка возврата ошибки` |
| `put` | `400` | `Старый и новый пароль обязательны` | `Если not old_password or not new_password` |

### [backend/api/admin/admin_excursions.py](../api/admin/admin_excursions.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `404` | `Экскурсия не найдена` | `Если not excursion` |
| `post` | `400` | `Фото не загружено` | `Если 'photo' not in request.files` |

### [backend/api/admin/admin_merch.py](../api/admin/admin_merch.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `404` | `Product not found` | `Если not product` |

### [backend/api/admin/admin_news.py](../api/admin/admin_news.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `404` | `Новость не найдена` | `Если not news` |
| `post` | `400` | `Фото не загружено` | `Если 'photo' not in request.files` |

### [backend/api/admin/admin_reservations.py](../api/admin/admin_reservations.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `404` | `Бронь не найдена` | `Если not reservation_data` |

### [backend/api/admin/admin_users.py](../api/admin/admin_users.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `404` | `Пользователь не найден` | `Ветка возврата ошибки` |
| `put` | `400` | `Пустой JSON` | `Если not data` |
| `put` | `404` | `Пользователь не найден` | `Если not user` |

### [backend/api/admin/decorators.py](../api/admin/decorators.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `admin_required` | `403` | `Доступ запрещен` | `Ветка возврата ошибки` |

### [backend/api/login/routes.py](../api/login/routes.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `post` | `400` | `Необходимо указать email и пароль` | `Если not email or not password` |
| `post` | `401` | `Неверный email или пароль` | `Если not user` |
| `post` | `401` | `Неверный email или пароль` | `Если not user.check_password(password)` |
| `post` | `500` | `Ошибка при генерации токена` | `Если not token` |

### [backend/api/references/ref_age_categories.py](../api/references/ref_age_categories.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `404*` | `Возрастная категория не найдена` | `Если not age_category` |
| `post` | `400*` | `Возрастная категория с таким именем уже существует` | `Если get_age_category_by_name(name)` |
| `post` | `400*` | `Поле name обязательно` | `Если not name` |

### [backend/api/references/ref_categories.py](../api/references/ref_categories.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `404*` | `Категория не найдена` | `Если not category` |
| `post` | `400*` | `Категория с таким именем уже существует` | `Если get_category_by_name(name)` |
| `post` | `400*` | `Поле name обязательно` | `Если not name` |

### [backend/api/references/ref_company_history.py](../api/references/ref_company_history.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `404*` | `Событие не найдено` | `Если not item` |
| `get` | `404*` | `Событие не найдено` | `Если not item` |
| `put` | `404*` | `Событие не найдено` | `Если not item` |

### [backend/api/references/ref_cultural_space.py](../api/references/ref_cultural_space.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `404*` | `Элемент не найден` | `Если not item` |
| `get` | `404*` | `Элемент не найден` | `Если not item` |
| `post` | `404*` | `Элемент не найден` | `Если not item` |
| `put` | `404*` | `Элемент не найден` | `Если not item` |

### [backend/api/references/ref_format_types.py](../api/references/ref_format_types.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `404*` | `Тип формата не найден` | `Если not format_type` |

### [backend/api/references/ref_partner.py](../api/references/ref_partner.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `404*` | `Партнёр не найден` | `Если not item` |
| `get` | `404*` | `Партнёр не найден` | `Если not item` |
| `post` | `404*` | `Партнёр не найден` | `Если not item` |
| `put` | `404*` | `Партнёр не найден` | `Если not item` |

### [backend/api/references/ref_projects.py](../api/references/ref_projects.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `404*` | `Проект не найден` | `Если not project` |
| `get` | `404*` | `Проект не найден` | `Если not project` |
| `put` | `404*` | `Проект не найден` | `Если not project` |

### [backend/api/references/ref_requisite.py](../api/references/ref_requisite.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `400*` | `Файл отсутствует` | `Если not item.file` |
| `delete` | `404*` | `Реквизит не найден` | `Если not item` |
| `get` | `404*` | `Реквизит не найден` | `Если not item` |
| `post` | `404*` | `Реквизит не найден` | `Если not item` |
| `put` | `404*` | `Реквизит не найден` | `Если not item` |

### [backend/api/references/ref_team.py](../api/references/ref_team.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete` | `404*` | `Сотрудник не найден` | `Если not member` |
| `get` | `404*` | `Сотрудник не найден` | `Если not member` |
| `post` | `404*` | `Сотрудник не найден` | `Если not member` |
| `put` | `404*` | `Сотрудник не найден` | `Если not member` |

### [backend/api/resident/decorators.py](../api/resident/decorators.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `resident_required` | `403` | `Доступ запрещён` | `Ветка возврата ошибки` |

### [backend/api/resident/resident_excursions.py](../api/resident/resident_excursions.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `404` | `Экскурсия не найдена` | `Если not excursion` |

### [backend/api/resident/resident_photos.py](../api/resident/resident_photos.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `post` | `400` | `Фото не загружено` | `Если 'photo' not in request.files` |

### [backend/api/user/user_merch.py](../api/user/user_merch.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `404` | `Product not found` | `Если not product` |
| `put` | `404` | `Cart item not found` | `Если not current_item` |

### [backend/api/user/user_news.py](../api/user/user_news.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `404` | `Новость не найдена` | `Если not news` |

### [backend/api/user/user_profile.py](../api/user/user_profile.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `post` | `400` | `Неверный или просроченный токен` | `Если not email` |
| `post` | `404` | `Пользователь не найден` | `Если not user` |

### [backend/api/user/user_reservations.py](../api/user/user_reservations.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `401` | `Пользователь не найден` | `Если not user` |
| `get` | `404` | `Бронирование не найдено` | `Если not reservation` |
| `get` | `404` | `Экскурсия не найдена` | `Если not excursion` |

### [backend/api/webhook/routes.py](../api/webhook/routes.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `post` | `400` | `Invalid webhook payload` | `Если not event_data or event_data.get('type') != 'notification' or 'event' not in event_data` |
| `post` | `400` | `Missing payment id` | `Если not payment_id` |
| `post` | `400` | `Missing refund id` | `Если not refund_id` |
| `post` | `400` | `Payment status verification failed` | `Если _object_value(trusted_payment, 'id') != payment_id or _object_value(trusted_payment, 'status') != expected_status` |
| `post` | `400` | `Refund status verification failed` | `Если _object_value(trusted_refund, 'id') != refund_id or _object_value(trusted_refund, 'status') != 'succeeded'` |
| `post` | `503` | `Could not verify payment` | `Перехвачено Exception` |
| `post` | `503` | `Could not verify refund` | `Перехвачено Exception` |

### [backend/api/yandex/routes.py](../api/yandex/routes.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get` | `400` | `Необходим параметр suggest` | `Если not suggest_query` |
| `get` | `500` | `Ошибка сервиса Яндекса: {str(e)}` | `Перехвачено Exception` |

### [backend/core/__init__.py](../core/__init__.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `handle_exception` | `500` | `Internal server error` | `Ветка возврата ошибки` |
| `handle_request_entity_too_large` | `413` | `Uploaded form data is too large` | `Ветка возврата ошибки` |

### [backend/core/services/event_services/event_api.py](../core/services/event_services/event_api.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `handle_create_event` | `400` | `Неверный JSON: {str(e)}` | `Перехвачено json.JSONDecodeError` |
| `handle_create_event` | `400` | `Поле '{data_field}' обязательно` | `Если data_field not in request.form` |

### [backend/core/services/event_services/event_crud.py](../core/services/event_services/event_crud.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_event` | `400` | `Место проведения обязательно` | `Если not data.get('place')` |
| `create_event` | `500` | `Ошибка при создании экскурсии: {str(e)}` | `Перехвачено Exception` |
| `create_event` | `исключение` | `Возрастная категория не найдена` | `Ветка возврата ошибки` |
| `create_event` | `исключение` | `Категория не найдена` | `Ветка возврата ошибки` |
| `create_event` | `исключение` | `Формат мероприятия не найден` | `Ветка возврата ошибки` |
| `delete_event` | `404` | `Экскурсия не найдена` | `Если not event` |
| `delete_event` | `500` | `Ошибка при удалении экскурсии: {str(e)}` | `Перехвачено Exception` |
| `update_event` | `400` | `Возрастная категория '{data['age_category']}' не найдена` | `Если not age_category` |
| `update_event` | `400` | `Категория '{data['category']}' не найдена` | `Если not category` |
| `update_event` | `400` | `Формат '{data['format_type']}' не найден` | `Если not format_type` |
| `update_event` | `404` | `Экскурсия не найдена` | `Если not event` |
| `update_event` | `500` | `Ошибка при обновлении экскурсии: {str(e)}` | `Перехвачено Exception` |
| `verify_resident_owns_event` | `403` | `У вас нет доступа к этой экскурсии` | `Если event.created_by != resident_id` |
| `verify_resident_owns_event` | `404` | `Экскурсия не найдена` | `Если not event` |

### [backend/core/services/event_services/event_photo_service.py](../core/services/event_services/event_photo_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `add_photo_to_event` | `400` | `Недопустимый файл` | `Если not photos` |
| `add_photo_to_event` | `400` | `Фото не загружено` | `Если not photo_file` |
| `add_photo_to_event` | `500` | `Ошибка при сохранении фото: {str(e)}` | `Перехвачено Exception` |
| `delete_photo_from_event` | `404` | `Фото не найдено` | `Если not photo` |
| `delete_photo_from_event` | `500` | `Ошибка при удалении фото: {str(e)}` | `Перехвачено Exception` |
| `get_photos_for_event` | `404` | `Экскурсия не найдена` | `Если not event` |

### [backend/core/services/event_services/event_session_service.py](../core/services/event_services/event_session_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_event_session` | `400` | `Неверный или отсутствует start_datetime` | `Перехвачено (KeyError, ValueError)` |
| `create_event_session` | `500` | `Ошибка при создании сессии: {str(e)}` | `Перехвачено Exception` |
| `delete_event_session` | `400` | `Ошибка возврата по брони {res.reservation_id}: {str(e)}` | `Перехвачено Exception` |
| `delete_event_session` | `404` | `Сессия не найдена` | `Если not session` |
| `delete_event_session` | `500` | `Ошибка при удалении сессии: {str(e)}` | `Перехвачено Exception` |
| `update_event_session` | `400` | `Неверный формат start_datetime` | `Перехвачено ValueError` |
| `update_event_session` | `404` | `Сессия не найдена` | `Если not session` |
| `update_event_session` | `500` | `Ошибка при обновлении сессии: {str(e)}` | `Перехвачено Exception` |

### [backend/core/services/merch_service.py](../core/services/merch_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `_collect_variants` | `исключение` | `Valid color is required for color sizes` | `Если not color` |
| `_resolve_variant_size` | `исключение` | `Valid size_id is required for each variant` | `Если not size` |
| `_resolve_variant_size` | `исключение` | `size_name is required for each variant` | `Ветка возврата ошибки` |
| `_sync_colors` | `исключение` | `Color name is required` | `Если not item.get('name')` |
| `_upsert_product_variant` | `исключение` | `Valid color_id is required for variant` | `Если not color or color.product_id != product.product_id` |
| `_upsert_product_variant` | `исключение` | `Variant belongs to another color` | `Если variant and color_id and (variant.color_id != color_id)` |
| `_upsert_product_variant` | `исключение` | `Variant belongs to another product` | `Если variant and variant.product_id != product.product_id` |
| `add_product_color` | `400` | `Color name is required` | `Если not data.get('name')` |
| `add_product_color` | `400` | `Product color or size conflicts with existing records` | `Перехвачено IntegrityError` |
| `add_product_color` | `404` | `Product not found` | `Если not product or product.is_deleted` |
| `add_product_color_size` | `400` | `Product size conflicts with existing records` | `Перехвачено IntegrityError` |
| `add_product_color_size` | `404` | `Color not found` | `Если not color` |
| `add_product_color_size` | `404` | `Product not found` | `Если not product or product.is_deleted` |
| `add_product_images` | `400` | `At least one image is required` | `Если not image_files` |
| `add_product_images` | `404` | `Product not found` | `Если not product or product.is_deleted` |
| `create_banner` | `400` | `image_path or image is required` | `Если not image_path` |
| `create_category` | `400` | `Category name or slug already exists` | `Перехвачено IntegrityError` |
| `create_category` | `400` | `name is required` | `Если not name` |
| `create_order` | `400` | `Cart contains unavailable products` | `Если not variant or not variant.product or (not variant.is_active) or variant.product.is_deleted or (not variant.product.is_active)` |
| `create_order` | `400` | `Cart is empty` | `Если not cart_items` |
| `create_order` | `400` | `Not enough stock` | `Если item.quantity > variant.stock` |
| `create_order` | `400` | `Only pickup delivery is supported` | `Если delivery_method != DELIVERY_PICKUP` |
| `create_order` | `400` | `pay_by_card is required` | `Если 'pay_by_card' not in data` |
| `create_order` | `400` | `{field} is required` | `Если not data.get(field)` |
| `create_order` | `502` | `Failed to create payment` | `Перехвачено Exception` |
| `create_product` | `400` | `Missing fields: {', '.join(missing)}` | `Если missing` |
| `create_product` | `400` | `Product data conflicts with existing records` | `Перехвачено IntegrityError` |
| `create_product` | `404` | `Category not found` | `Если not category` |
| `delete_banner` | `404` | `Banner not found` | `Если not banner` |
| `delete_cart_item` | `404` | `Cart item not found` | `Если not item` |
| `delete_category` | `400` | `Category has products` | `Если category.products` |
| `delete_category` | `404` | `Category not found` | `Если not category` |
| `delete_product` | `404` | `Product not found` | `Если not product or product.is_deleted` |
| `delete_product_image` | `404` | `Image not found` | `Если not image or not image.product or image.product.is_deleted` |
| `list_product_images` | `404` | `Product not found` | `Если not product or product.is_deleted` |
| `parse_json_payload` | `вызывающий код` | `Invalid JSON payload` | `Если not isinstance(raw_data, str)` |
| `parse_json_payload` | `вызывающий код` | `Invalid JSON payload` | `Перехвачено json.JSONDecodeError` |
| `parse_json_payload` | `вызывающий код` | `JSON payload must be an object` | `Если not isinstance(data, dict)` |
| `toggle_favorite` | `404` | `Product not found` | `Если not product or product.is_deleted or (not product.is_active)` |
| `update_banner` | `404` | `Banner not found` | `Если not banner` |
| `update_category` | `400` | `Category name or slug already exists` | `Перехвачено IntegrityError` |
| `update_category` | `404` | `Category not found` | `Если not category` |
| `update_order_status` | `404` | `Order not found` | `Если not order` |
| `update_product` | `400` | `Product data conflicts with existing records` | `Перехвачено IntegrityError` |
| `update_product` | `404` | `Category not found` | `Если not category` |
| `update_product` | `404` | `Product not found` | `Если not product or product.is_deleted` |
| `update_product_image` | `404` | `Image not found` | `Если not image or not image.product or image.product.is_deleted` |
| `upsert_cart_item` | `400` | `Not enough stock` | `Если quantity > variant.stock` |
| `upsert_cart_item` | `400` | `quantity must be greater than zero` | `Если quantity < 1` |
| `upsert_cart_item` | `404` | `Variant not found` | `Если not variant or not variant.product or (not variant.is_active) or variant.product.is_deleted or (not variant.product.is_active)` |

### [backend/core/services/news_service/news_image_service.py](../core/services/news_service/news_image_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `add_photo_to_news` | `404` | `Новость не найдена` | `Если not news` |
| `add_photo_to_news` | `500` | `Ошибка при добавлении фото: {str(e)}` | `Перехвачено Exception` |
| `delete_photo_from_news` | `404` | `Фото не найдено` | `Если not photo` |
| `delete_photo_from_news` | `500` | `Ошибка при удалении фото: {str(e)}` | `Перехвачено Exception` |
| `get_photos_for_news` | `404` | `Новость не найдена` | `Если not news` |

### [backend/core/services/news_service/news_service.py](../core/services/news_service/news_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_news_with_images` | `400` | `Неверный формат даты` | `Перехвачено ValueError` |
| `create_news_with_images` | `400` | `Ошибка в JSON: {str(e)}` | `Перехвачено json.JSONDecodeError` |
| `create_news_with_images` | `400` | `Поле 'data' обязательно` | `Если not data_str` |
| `create_news_with_images` | `400` | `Поля title и content обязательны` | `Если not all([title, content])` |
| `create_news_with_images` | `404` | `Пользователь не найден` | `Если not user` |
| `delete_news` | `вызывающий код` | `Новость не найдена` | `Если not news` |
| `update_news` | `400*` | `Неверный формат даты` | `Перехвачено ValueError` |
| `update_news` | `400*` | `Ошибка в JSON: {str(e)}` | `Перехвачено json.JSONDecodeError` |
| `update_news` | `400*` | `Поле 'data' обязательно` | `Если 'data' not in form_data` |
| `update_news` | `404*` | `Новость не найдена` | `Если not news` |

### [backend/core/services/ref_service/company_history_service.py](../core/services/ref_service/company_history_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `_parse_history_date` | `400*` | `Неверный формат даты. Используйте YYYY-MM-DD` | `Перехвачено ValueError` |
| `validate_history_data` | `400*` | `Поле date обязательно` | `Если not date_str` |
| `validate_history_data` | `400*` | `Поле description обязательно` | `Если not description` |
| `validate_history_data` | `400*` | `Поле title обязательно` | `Если not title` |

### [backend/core/services/ref_service/company_project_service.py](../core/services/ref_service/company_project_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_project` | `400*` | `Поле link обязательно` | `Если not link` |
| `create_project` | `400*` | `Поле title обязательно` | `Если not title` |
| `update_project` | `400*` | `Поле link обязательно` | `Если not link` |
| `update_project` | `400*` | `Поле title обязательно` | `Если not title` |

### [backend/core/services/ref_service/cultural_space_service.py](../core/services/ref_service/cultural_space_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_cultural_space` | `400*` | `Поле text обязательно` | `Если not text` |
| `delete_cultural_space_photo` | `400*` | `Фото отсутствует` | `Если not item.photo` |
| `delete_cultural_space_photo` | `404*` | `Элемент не найден` | `Если not item` |
| `update_cultural_space` | `400*` | `Поле text обязательно` | `Если not text` |
| `upload_cultural_space_photo` | `400*` | `Файл не выбран` | `Если not photo` |

### [backend/core/services/ref_service/format_type_service.py](../core/services/ref_service/format_type_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_format_type` | `400*` | `Поле name обязательно` | `Если not name` |
| `create_format_type` | `400*` | `Тип формата с таким именем уже существует` | `Если FormatType.query.filter_by(format_type_name=name).first()` |

### [backend/core/services/ref_service/partner_service.py](../core/services/ref_service/partner_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_partner` | `400*` | `Поле name обязательно` | `Если not name` |
| `delete_partner_photo` | `400*` | `Фото отсутствует` | `Если not partner.photo` |
| `delete_partner_photo` | `404*` | `Партнёр не найден` | `Если not partner` |
| `update_partner` | `400*` | `Поле name обязательно` | `Если not name` |
| `upload_partner_photo` | `400*` | `Файл не выбран` | `Если not photo` |

### [backend/core/services/ref_service/requisite_service.py](../core/services/ref_service/requisite_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_requisite` | `400*` | `Название обязательно` | `Если not title` |
| `create_requisite` | `400*` | `Файл обязателен` | `Если not file` |
| `replace_requisite_file` | `400*` | `Файл не выбран` | `Если not file` |
| `update_requisite` | `400*` | `Название обязательно` | `Если not title` |

### [backend/core/services/ref_service/team_service.py](../core/services/ref_service/team_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `_validate_and_save_photo` | `400*` | `Файл не выбран` | `Если not photo or not photo.filename` |
| `create_team_member` | `400*` | `Поле full_name обязательно` | `Если not full_name` |
| `delete_team_photo` | `400*` | `Фото отсутствует` | `Если not member.photo` |
| `update_team_member` | `400*` | `Поле full_name обязательно` | `Если not full_name` |

### [backend/core/services/ref_service/trust_reason_service.py](../core/services/ref_service/trust_reason_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_trust_reason` | `400*` | `Поле title обязательно` | `Если not title` |
| `delete_trust_reason` | `404*` | `Причина не найдена` | `Если not reason` |

### [backend/core/services/reservation_service/reservation_cancel.py](../core/services/reservation_service/reservation_cancel.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `cancel_user_reservation` | `400` | `reservation_id is required` | `Если not reservation_id` |
| `cancel_user_reservation` | `400` | `Бронирование уже отменено` | `Если reservation.is_cancelled` |
| `cancel_user_reservation` | `401` | `Пользователь не найден` | `Если not user` |
| `cancel_user_reservation` | `404` | `Бронирование не найдено или не принадлежит вам` | `Если not reservation or reservation.user_id != user.user_id` |
| `cancel_user_reservation` | `500` | `Не удалось сделать возврат средств` | `Перехвачено Exception` |

### [backend/core/services/reservation_service/reservation_crud.py](../core/services/reservation_service/reservation_crud.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `create_reservation_with_payment` | `400` | `session_id is required` | `Если not session_id` |
| `create_reservation_with_payment` | `400` | `Количество участников должно быть положительным целым числом` | `Если isinstance(participants_count, bool) or not isinstance(participants_count, int) or participants_count < 1` |
| `create_reservation_with_payment` | `400` | `Нельзя забронировать прошедший сеанс` | `Если session.start_datetime <= datetime.now()` |
| `create_reservation_with_payment` | `400` | `Событие недоступно для бронирования` | `Если not session.event or not session.event.is_active` |
| `create_reservation_with_payment` | `401` | `Пользователь не найден` | `Если not user` |
| `create_reservation_with_payment` | `404` | `Сеанс не найден` | `Если not session` |
| `create_reservation_with_payment` | `409` | `Недостаточно свободных мест` | `Если held_participants + participants_count > session.max_participants` |
| `create_reservation_with_payment` | `409` | `У вас уже есть активное бронирование на этот сеанс` | `Если duplicate` |
| `create_reservation_with_payment` | `502` | `Не удалось создать платёж` | `Перехвачено Exception` |
| `delete_reservation_with_refund` | `400` | `Не удалось вернуть средства, статус возврата: {refund.status}` | `Если refund.status != 'succeeded'` |
| `delete_reservation_with_refund` | `404` | `Бронь не найдена` | `Если not reservation` |
| `delete_reservation_with_refund` | `500` | `Ошибка при попытке возврата средств: {str(e)}` | `Перехвачено Exception` |
| `delete_reservation_with_refund` | `500` | `Ошибка при удалении брони: {str(e)}` | `Перехвачено Exception` |

### [backend/core/services/user_services/auth_service.py](../core/services/user_services/auth_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `change_profile_password` | `400` | `Оба поля обязательны` | `Если not old_password or not new_password` |
| `change_profile_password` | `401` | `Неверный текущий пароль` | `Если not user.check_password(old_password)` |
| `change_profile_password` | `404` | `Пользователь не найден` | `Если not user` |
| `login_user` | `400` | `Необходимо указать и email, и пароль` | `Если not email or not password` |
| `login_user` | `401` | `Неверный email или пароль` | `Если not user` |
| `login_user` | `401` | `Неверный email или пароль` | `Если not user.check_password(password)` |
| `login_user` | `403` | `Доступ запрещён для этой роли` | `Если user.role != role` |
| `login_user` | `500` | `Ошибка при генерации токена` | `Если not token` |
| `register_user` | `400` | `Необходимо указать email, пароль и полное имя` | `Если not email or not password or (not full_name)` |
| `register_user` | `400` | `Номер телефона не должен превышать 32 символа` | `Если phone and len(phone) > 32` |
| `register_user` | `409` | `Пользователь с таким именем или почтой уже существует либо роль недопустима` | `Если not new_user` |

### [backend/core/services/user_services/profile_service.py](../core/services/user_services/profile_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `get_profile` | `404` | `Пользователь не найден` | `Если not user` |
| `get_user_info_response` | `404` | `Пользователь не найден` | `Если not user` |

### [backend/core/services/user_services/user_service.py](../core/services/user_services/user_service.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `delete_user` | `400*` | `Невозможно удалить пользователя: у него есть {active_reservations} активных бронирований` | `Если active_reservations > 0` |
| `delete_user` | `400*` | `Невозможно удалить пользователя: у него есть {created_events} созданных экскурсий` | `Если created_events > 0` |
| `delete_user` | `404*` | `Пользователь не найден` | `Если not user` |
| `update_profile` | `400` | `Этот email уже используется` | `Если User.query.filter_by(email=new_email).first()` |
| `update_profile` | `404` | `Пользователь не найден` | `Если not user` |
| `update_user` | `исключение` | `Email уже используется другим пользователем` | `Если existing` |
| `update_user` | `исключение` | `Роль '{role_name}' не найдена. Допустимые значения: admin, resident, user` | `Перехвачено (TypeError, ValueError)` |

### [backend/core/utilits/file_utils.py](../core/utilits/file_utils.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `_validate_image` | `400*` | `Недопустимый формат изображения` | `Если not original_filename or extension not in configured_extensions or extension not in IMAGE_SIGNATURES` |
| `_validate_image` | `400*` | `Размер изображения должен быть от 1 байта до 5 МБ` | `Если size <= 0 or size > MAX_IMAGE_BYTES` |
| `_validate_image` | `400*` | `Содержимое файла не соответствует формату изображения` | `Если not matcher(header)` |
| `validate_image_upload` | `400*` | `Размер файла не должен превышать 5 MB` | `Если size > MAX_IMAGE_BYTES` |
| `validate_image_upload` | `400*` | `Файл должен быть изображением` | `Если not file.content_type.startswith('image/')` |

### [backend/core/utilits/request_utils.py](../core/utilits/request_utils.py)

| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |
|---|---|---|---|
| `require_json_object` | `400*` | `JSON должен содержать объект` | `Если not isinstance(value, dict)` |

<!-- END GENERATED ERROR CATALOG -->
