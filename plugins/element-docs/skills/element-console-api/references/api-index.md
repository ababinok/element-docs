# Console API Index

Generated from the local Docusaurus HTML archive and decoded `frontMatter.api` payloads.

## Авторизация и аутентификация

- `POST /console/sys/token` - Получить токен доступа (`post-console-sys-token`)

## Веб-адреса приложения

- `GET /console/api/v2/applications/{ApplicationId}/endpoints` - Получить веб-адреса приложения (`get-console-api-v-2-applications-application-id-endpoints`)
- `POST /console/api/v2/applications/{ApplicationId}/endpoints` - Создать веб-адрес приложения (`post-console-api-v-2-applications-application-id-endpoints`)
- `GET /console/api/v2/applications/{ApplicationId}/endpoints/{EndpointId}` - Получить информацию о веб-адресе по его идентификатору (`get-console-api-v-2-applications-application-id-endpoints-endpoint-id`)
- `DELETE /console/api/v2/applications/{ApplicationId}/endpoints/{EndpointId}` - Удалить веб-адрес по его идентификатору (`delete-console-api-v-2-applications-application-id-endpoints-endpoint-id`)
- `GET /console/api/v2/applications/{ApplicationId}/endpoints/{EndpointId}/certificates` - Получить все сертификаты, которые можно привязать к данному веб-адресу (`get-console-api-v-2-applications-application-id-endpoints-endpoint-id-certificates`)
- `POST /console/api/v2/applications/{ApplicationId}/endpoints/{EndpointId}/certificates` - Создать, проверить и привязать сертификат (`post-console-api-v-2-applications-application-id-endpoints-endpoint-id-certificates`)
- `POST /console/api/v2/applications/{ApplicationId}/endpoints/{EndpointId}/certificates/{CertificateId}` - Привязать сертификат к веб-адресу приложения (`post-console-api-v-2-applications-application-id-endpoints-endpoint-id-certificates-certificate-id`)
- `GET /console/api/v2/applications/{ApplicationId}/certificates` - Получить все сертификаты, которые можно привязать к данному приложению (`get-console-api-v-2-applications-application-id-certificates`)
- `POST /console/api/v2/applications/{ApplicationId}/certificates` - Создать и проверить сертификат (`post-console-api-v-2-applications-application-id-certificates`)
- `GET /console/api/v2/applications/{ApplicationId}/certificates/{CertificateId}` - Получить сертификат по идентификатору (`get-console-api-v-2-applications-application-id-certificates-certificate-id`)
- `GET /console/api/v2/applications/{ApplicationId}/endpoint-validation` - Проверить возможность привязки нового веб-адреса к приложению (`get-console-api-v-2-applications-application-id-endpoint-validation`)
- `PUT /console/api/v2/applications/{ApplicationId}/endpoints/{EndpointId}/certificate-type` - Сменить тип сертификата (`put-console-api-v-2-applications-application-id-endpoints-endpoint-id-certificate-type`)

## Групповая разработка. Ветки

- `GET /console/api/v2/branches` - Получить список веток (`get-console-api-v-2-branches`)
- `POST /console/api/v2/branches` - Создать новую ветку (`post-console-api-v-2-branches`)
- `PUT /console/api/v2/branches` - Создать новую ветку или обновить уже созданную (`put-console-api-v-2-branches`)
- `DELETE /console/api/v2/branches` - Удалить ветку по имени (`delete-console-api-v-2-branches`)
- `GET /console/api/v2/branches/{id}` - Получить ветку (`get-console-api-v-2-branches-id`)
- `PUT /console/api/v2/branches/{id}` - Изменить ветку (`put-console-api-v-2-branches-id`)
- `DELETE /console/api/v2/branches/{id}` - Удалить ветку (`delete-console-api-v-2-branches-id`)

## Групповая разработка. Задачи

- `GET /console/api/v2/issues` - Получить список задач (`get-console-api-v-2-issues`)
- `POST /console/api/v2/issues` - Создать новую задачу (`post-console-api-v-2-issues`)
- `PUT /console/api/v2/issues` - Создать или обновить задачу (`put-console-api-v-2-issues`)
- `GET /console/api/v2/issues/{key}` - Получить задачу (`get-console-api-v-2-issues-key`)
- `PUT /console/api/v2/issues/{key}` - Изменить задачу (`put-console-api-v-2-issues-key`)
- `DELETE /console/api/v2/issues/{key}` - Удалить задачу (`delete-console-api-v-2-issues-key`)
- `GET /console/api/v2/issues/{key}/hyperlink` - Получить http ссылку на задачу (`get-console-api-v-2-issues-key-hyperlink`)
- `GET /console/api/v2/issues/{key}/attachment/{name}` - Получить файл вложения (`get-console-api-v-2-issues-key-attachment`)
- `POST /console/api/v2/issues/{key}/attachment/{name}` - Добавить файл вложения (`post-console-api-v-2-issues-key-attachment`)
- `PUT /console/api/v2/issues/{key}/attachment/{name}` - Заполнить файл вложения (`put-console-api-v-2-issues-key-attachment`)
- `DELETE /console/api/v2/issues/{key}/attachment/{name}` - Удалить файл вложения (`delete-console-api-v-2-issues-key-attachment`)
- `GET /console/api/v2/issues/{key}/description` - Получить полный текст описания задачи (`get-console-api-v-2-issues-key-description`)
- `PUT /console/api/v2/issues/{key}/description` - Заполнить полный текст описания задачи (`put-console-api-v-2-issues-key-description`)
- `GET /console?state=route/issue/create/number:{number}/title:{title}/project-id:{project-id}` - Создать задачу по гиперссылке (`get-console-route-issues-create`)

## Задачи

- `GET /console/api/v2/tasks/group-tasks` - Получить список групповых задач (`get-applications-paa-s-api-v-2-group-tasks`)
- `POST /console/api/v2/tasks/group-tasks/update-applications-project` - Создать групповую задачу обновления сборки приложений (`post-applications-paa-s-api-v-2-group-tasks-update-applications-project`)
- `POST /console/api/v2/tasks/group-tasks/update-applications-technology` - Создать групповую задачу обновления версии технологии приложений (`post-applications-paa-s-api-v-2-group-tasks-update-applications-technology`)
- `GET /console/api/v2/tasks/group-tasks/{taskId}` - Получить групповую задачу (`get-applications-paa-s-api-v-2-group-tasks-task-id`)
- `GET /console/api/v2/tasks/application-tasks` - Получить список задач приложений (`get-applications-paa-s-api-v-2-application-tasks`)
- `GET /console/api/v2/tasks/application-tasks/{taskId}` - Узнать о задаче (`get-applications-paa-s-api-v-2-application-tasks-task-id`)
- `GET /console/api/v2/tasks/deployment-instance-tasks` - Получить список задач экземпляров серверов (`get-applications-paa-s-api-v-2-deployment-instance-tasks`)
- `GET /console/api/v2/tasks/deployment-instance-tasks/{taskId}` - Узнать о задаче экземпляра сервера (`get-applications-paa-s-api-v-2-deployment-instance-tasks-task-id`)

## Команды API


## Пользователи

- `GET /console/api/v2/user-lists` - Получить списки пользователей (`get-console-api-v-2-user-lists`)
- `POST /console/api/v2/user-lists` - Создать список пользователей (`post-console-api-v-2-user-lists`)
- `GET /console/api/v2/user-lists/{UserListId}` - Получить список пользователей (`get-console-api-v-2-user-lists-user-list-id`)
- `DELETE /console/api/v2/user-lists/{UserListId}` - Удалить список пользователей (`delete-console-api-v-2-user-lists-user-list-id`)
- `GET /console/api/v2/user-lists/{UserListId}/settings/sms-gateways` - Получить СМС-шлюзы (`get-console-api-v-2-user-lists-user-list-id-settings-sms-gateways`)
- `POST /console/api/v2/user-lists/{UserListId}/settings/sms-gateways` - Создать СМС-шлюз (`post-console-api-v-2-user-lists-user-list-id-settings-sms-gateways`)
- `PUT /console/api/v2/user-lists/{UserListId}/settings/sms-gateways/{GatewayId}` - Обновить СМС-шлюз (`put-console-api-v-2-user-lists-user-list-id-settings-sms-gateways-gateway-id`)
- `DELETE /console/api/v2/user-lists/{UserListId}/settings/sms-gateways/{GatewayId}` - Удалить СМС-шлюз (`delete-console-api-v-2-user-lists-user-list-id-settings-sms-gateways-gateway-id`)
- `GET /console/api/v2/user-lists/{UserListId}/settings/smtp-gateways` - Получить почтовые шлюзы (`get-console-api-v-2-user-lists-user-list-id-settings-smtp-gateways`)
- `POST /console/api/v2/user-lists/{UserListId}/settings/smtp-gateways` - Создать почтовый шлюз (`post-console-api-v-2-user-lists-user-list-id-settings-smtp-gateways`)
- `PUT /console/api/v2/user-lists/{UserListId}/settings/smtp-gateways/{GatewayId}` - Обновить почтовый шлюз (`put-console-api-v-2-user-lists-user-list-id-settings-smtp-gateways-gateway-id`)
- `DELETE /console/api/v2/user-lists/{UserListId}/settings/smtp-gateways/{GatewayId}` - Удалить почтовый шлюз (`delete-console-api-v-2-user-lists-user-list-id-settings-smtp-gateways-gateway-id`)
- `GET /console/api/v2/user-lists/{UserListId}/settings/password-policy` - Узнать о политике паролей (`get-console-api-v-2-user-lists-user-list-id-settings-password-policy`)
- `PUT /console/api/v2/user-lists/{UserListId}/settings/password-policy` - Обновить политику паролей (`put-console-api-v-2-user-lists-user-list-id-settings-password-policy`)
- `POST /console/api/v2/user-lists/{UserListId}/settings/password-policy/enable` - Включить политику паролей (`post-console-api-v-2-user-lists-user-list-id-settings-password-policy-enable`)
- `POST /console/api/v2/user-lists/{UserListId}/settings/password-policy/disable` - Отключить политику паролей (`post-console-api-v-2-user-lists-user-list-id-settings-password-policy-disable`)
- `POST /console/api/v2/user-lists/{UserListId}/settings/include-personal-data-in-messages/enable` - Использовать персональные данные (`post-console-api-v-2-user-lists-user-list-id-settings-include-personal-data-in-messages-enable`)
- `POST /console/api/v2/user-lists/{UserListId}/settings/include-personal-data-in-messages/disable` - Не использовать персональные данные (`post-console-api-v-2-user-lists-user-list-id-settings-include-personal-data-in-messages-disable`)
- `GET /console/api/v2/user-lists/{UserListId}/settings/confirmations` - Получить способы подтверждения пользователей (`get-console-api-v-2-user-lists-user-list-id-settings-confirmations`)
- `PUT /console/api/v2/user-lists/{UserListId}/settings/confirmations` - Обновить способы подтверждения пользователей (`put-console-api-v-2-user-lists-user-list-id-settings-confirmations`)
- `GET /console/api/v2/user-lists/{UserListId}/settings/self-registration` - Получить настройки самостоятельной регистрации (`get-console-api-v-2-user-lists-user-list-id-settings-self-registration`)
- `PUT /console/api/v2/user-lists/{UserListId}/settings/self-registration` - Обновить настройки самостоятельной регистрации (`put-console-api-v-2-user-lists-user-list-id-settings-self-registration`)
- `GET /console/api/v2/user-lists/{UserListId}/settings/account-services-settings` - Получить настройки сервисов внешних учетных записей (`get-console-api-v-2-user-lists-user-list-id-settings-account-services-settings`)
- `POST /console/api/v2/user-lists/{UserListId}/settings/account-services-settings` - Установить настройки сервиса внешних учетных записей (`post-console-api-v-2-user-lists-user-list-id-settings-account-services-settings`)
- `PUT /console/api/v2/user-lists/{UserListId}/settings/account-services-settings/{AccountServiceId}` - Обновить настройки сервиса внешних учетных записей (`put-console-api-v-2-user-lists-user-list-id-settings-account-services-settings-account-service-id`)
- `DELETE /console/api/v2/user-lists/{UserListId}/settings/account-services-settings/{AccountServiceId}` - Удалить настройки сервиса внешних учетных записей (`delete-console-api-v-2-user-lists-user-list-id-settings-account-services-settings-account-service-id`)
- `GET /console/api/v2/user-lists/{UserListId}/users` - Получить пользователей (`get-console-api-v-2-user-lists-user-list-id-users`)
- `POST /console/api/v2/user-lists/{UserListId}/users` - Создать пользователя (`post-console-api-v-2-user-lists-user-list-id-users`)
- `GET /console/api/v2/user-lists/{UserListId}/users/{UserId}` - Получить пользователя (`get-console-api-v-2-user-lists-user-list-id-users-user-id`)
- `PUT /console/api/v2/user-lists/{UserListId}/users/{UserId}` - Обновить информацию о пользователе (`put-console-api-v-2-user-lists-user-list-id-users-user-id`)
- `DELETE /console/api/v2/user-lists/{UserListId}/users/{UserId}` - Удалить пользователя (`delete-console-api-v-2-user-lists-user-list-id-users-user-id`)
- `GET /console/api/v2/user-lists/{UserListId}/users/{UserId}/access-tokens` - Получить список токенов доступа (`get-console-api-v-2-user-lists-user-list-id-users-user-id-access-tokens`)
- `POST /console/api/v2/user-lists/{UserListId}/users/{UserId}/access-tokens` - Создать токен доступа (`post-console-api-v-2-user-lists-user-list-id-users-user-id-access-tokens`)
- `DELETE /console/api/v2/user-lists/{UserListId}/users/{UserId}/access-tokens/{ClientId}` - Удалить токен доступа (`delete-console-api-v-2-user-lists-user-list-id-users-user-id-access-tokens-client-id`)
- `POST /console/api/v2/user-lists/{UserListId}/users/{UserId}/reset-password` - Сбросить пароль пользователя (`post-console-api-v-2-user-lists-user-list-id-users-user-id-reset-password`)
- `GET /console/api/v2/user-lists/{UserListId}/users/{UserId}/esia-account` - Получить учетную запись ЕСИА (`get-console-api-v-2-user-lists-user-list-id-users-user-id-esia-account`)
- `POST /console/api/v2/user-lists/{UserListId}/users/{UserId}/esia-account` - Добавить учетную запись ЕСИА (`post-console-api-v-2-user-lists-user-list-id-users-user-id-esia-account`)
- `PUT /console/api/v2/user-lists/{UserListId}/users/{UserId}/esia-account` - Обновить учетную запись ЕСИА (`put-console-api-v-2-user-lists-user-list-id-users-user-id-esia-account`)
- `DELETE /console/api/v2/user-lists/{UserListId}/users/{UserId}/esia-account` - Удалить учетную запись ЕСИА (`delete-console-api-v-2-user-lists-user-list-id-users-user-id-esia-account`)
- `GET /console/api/v2/user-lists/{UserListId}/users/{UserId}/accounts` - Получить учетные записи (`get-console-api-v-2-user-lists-user-list-id-users-user-id-accounts`)
- `POST /console/api/v2/user-lists/{UserListId}/users/{UserId}/accounts` - Добавить учетную запись (`post-console-api-v-2-user-lists-user-list-id-users-user-id-accounts`)
- `DELETE /console/api/v2/user-lists/{UserListId}/users/{UserId}/accounts/{AccountId}/service/{ServiceId}` - Удалить учетную запись (`delete-console-api-v-2-user-lists-user-list-id-users-user-id-accounts-account-id-service-service-id`)
- `GET /console/api/v2/user-lists/{UserListId}/users/{UserId}/2fa` - Получить настройки двухфакторной аутентификации (`get-console-api-v-2-user-lists-user-list-id-users-user-id-2-fa`)
- `PUT /console/api/v2/user-lists/{UserListId}/users/{UserId}/2fa` - Обновить настройки двухфакторной аутентификации (`put-console-api-v-2-user-lists-user-list-id-users-user-id-2-fa`)
- `POST /console/api/v2/user-lists/{UserListId}/users/{UserId}/2fa/enable` - Использовать двухфакторную аутентификацию (`post-console-api-v-2-user-lists-user-list-id-users-user-id-2-fa-enable`)
- `POST /console/api/v2/user-lists/{UserListId}/users/{UserId}/2fa/disable` - Не использовать двухфакторную аутентификацию (`post-console-api-v-2-user-lists-user-list-id-users-user-id-2-fa-disable`)

## Приложения

- `GET /console/api/v2/applications` - Получить список приложений (`get-console-api-v-2-applications`)
- `POST /console/api/v2/applications` - Создать приложение (`post-console-api-v-2-applications`)
- `GET /console/api/v2/applications/{ApplicationId}` - Получить приложение (`get-console-api-v-2-applications-application-id`)
- `DELETE /console/api/v2/applications/{ApplicationId}` - Удалить приложение (`delete-console-api-v-2-applications-application-id`)
- `GET /console/api/v2/applications/{ApplicationId}/dumps` - Получить список дампов приложения (`get-console-api-v-2-applications-application-id-dumps`)
- `POST /console/api/v2/applications/{ApplicationId}/dumps` - Создать дамп приложения (`post-console-api-v-2-applications-application-id-dumps`)
- `GET /console/api/v2/applications/{ApplicationId}/dumps/{dumpsId}` - Получить дамп приложения (`get-console-api-v-2-applications-application-id-dumps-dumps-id`)
- `PUT /console/api/v2/applications/{ApplicationId}/dumps/{dumpsId}` - Изменить дамп приложения (`put-console-api-v-2-applications-application-id-dumps-dumps-id`)
- `DELETE /console/api/v2/applications/{ApplicationId}/dumps/{dumpsId}` - Удалить дамп приложения (`delete-console-api-v-2-applications-application-id-dumps-dumps-id`)
- `POST /console/api/v2/applications/{ApplicationId}/dumps/{dumpId}/export` - Экспортировать дамп приложения (`post-console-api-v-2-applications-application-id-dumps-dump-id-export`)
- `GET /console/api/v2/applications/{ApplicationId}/users` - Получить всех пользователей приложения (`get-console-api-v-2-applications-application-id-users`)
- `POST /console/api/v2/applications/{ApplicationId}/users` - Подключить пользователя к приложению (`post-console-api-v-2-applications-application-id-users`)
- `PUT /console/api/v2/applications/{ApplicationId}/users/{UserListId}/{UserId}` - Изменить статус пользователя как администратора (`put-console-api-v-2-applications-application-id-users-user-list-id-user-id`)
- `DELETE /console/api/v2/applications/{ApplicationId}/users/{UserListId}/{UserId}` - Отключить пользователя от приложения (`delete-console-api-v-2-applications-application-id-users-user-list-id-user-id`)
- `POST /console/api/v2/applications/{ApplicationId}/users/check-can-connect-user` - Проверить возможность подключения пользователя (`post-console-api-v-2-applications-application-id-users-check-can-connect-user`)
- `PUT /console/api/v2/applications/{ApplicationId}/users/change-token-access` - Изменить настройки доступа пользователя к HTTP сервисам (`put-console-api-v-2-applications-application-id-users-change-token-access`)
- `GET /console/api/v2/applications/{ApplicationId}/project` - Узнать о проекте приложения (`get-console-api-v-2-applications-application-id-project`)
- `POST /console/api/v2/applications/{ApplicationId}/project/export` - Экспортировать проект приложения (`post-console-api-v-2-applications-application-id-project-export`)
- `POST /console/api/v2/applications/{ApplicationId}/project/update` - Обновить версию приложения (`post-console-api-v-2-applications-application-id-project-update`)
- `POST /console/api/v2/applications/{ApplicationId}/project/reapply` - Переиспользовать проект приложения (`post-console-api-v-2-applications-application-id-project-reapply`)
- `GET /console/api/v2/applications/{ApplicationId}/status` - Узнать о состоянии приложения (`get-console-api-v-2-applications-application-id-status`)
- `PUT /console/api/v2/applications/{ApplicationId}/status/suspend` - Заморозить приложение (`post-console-api-v-2-applications-application-id-status-suspend`)
- `PUT /console/api/v2/applications/{ApplicationId}/status/restore` - Разморозить приложение (`post-console-api-v-2-applications-application-id-status-restore`)
- `PUT /console/api/v2/applications/{ApplicationId}/status/start` - Запустить приложение (`post-console-api-v-2-applications-application-id-status-start`)
- `PUT /console/api/v2/applications/{ApplicationId}/status/stop` - Остановить приложение (`post-console-api-v-2-applications-application-id-status-stop`)
- `POST /console/api/v2/applications/{ApplicationId}/status/convert` - Конвертировать приложение (`post-console-api-v-2-applications-application-id-status-convert`)
- `GET /console/api/v2/applications/{ApplicationId}/technology` - Узнать версию технологии приложения (`get-console-api-v-2-applications-application-id-technology`)
- `GET /console/api/v2/applications/{ApplicationId}/technology/deployment-instance` - Узнать об экземпляре размещения технологии приложения (`get-console-api-v-2-applications-application-id-technology-deployment-instance`)
- `GET /console/api/v2/applications/{ApplicationId}/userlists` - Получить списки пользователей приложения (`get-console-api-v-2-applications-application-id-userlists`)
- `POST /console/api/v2/applications/{ApplicationId}/userlists` - Подключить списки пользователей к приложению (`post-console-api-v-2-applications-application-id-userlists`)
- `DELETE /console/api/v2/applications/{ApplicationId}/userlists` - Отключить списки пользователей от приложения (`delete-console-api-v-2-applications-application-id-userlists`)
- `DELETE /console/api/v2/applications/{ApplicationId}/userlists/{UserListId}` - Отключить список пользователей от приложения по идентификатору (`delete-console-api-v-2-applications-application-id-userlists-user-list-id`)
- `POST /console/api/v2/applications/{ApplicationId}/actions/debug` - Получить данные для отладки приложения (`post-console-api-v-2-applications-application-id-actions-debug`)
- `POST /console/api/v2/applications/{ApplicationId}/actions/recompute-rights` - Пересчитать права доступа к приложению (`post-console-api-v-2-applications-application-id-actions-recompute-rights`)
- `POST /console/api/v2/applications/{ApplicationId}/actions/autostarting-processes/start` - Начать автозапуск процессов приложения (`post-console-api-v-2-applications-application-id-actions-autostarting-processes-start`)
- `POST /console/api/v2/applications/{ApplicationId}/actions/autostarting-processes/stop` - Остановить автозапуск процессов приложения (`post-console-api-v-2-applications-application-id-actions-autostarting-processes-stop`)
- `GET /console/api/v2/applications/{ApplicationId}/account-services-settings` - Получить настройки сервисов внешних учетных записей (`get-console-api-v-2-applications-application-id-account-services-settings`)
- `POST /console/api/v2/applications/{ApplicationId}/account-services-settings` - Установить настройки сервиса внешних учетных записей (`post-console-api-v-2-applications-application-id-account-services-settings`)
- `PUT /console/api/v2/applications/{ApplicationId}/account-services-settings/{AccountServiceId}` - Обновить настройки сервиса внешних учетных записей (`put-console-api-v-2-applications-application-id-account-services-settings-account-service-id`)
- `DELETE /console/api/v2/applications/{ApplicationId}/account-services-settings/{AccountServiceId}` - Удалить настройки сервиса внешних учетных записей (`delete-console-api-v-2-applications-application-id-account-services-settings-account-service-id`)
- `GET /console/api/v2/applications/{ApplicationId}/allowed-auths` - Получить разрешенные способы входа в приложение (`get-console-api-v-2-applications-application-id-allowed-auths`)
- `PUT /console/api/v2/applications/{ApplicationId}/allowed-auths` - Обновить разрешенные способы входа в приложение (`put-console-api-v-2-applications-application-id-allowed-auths`)
- `GET /console/api/v2/applications/{ApplicationId}/schedulings` - Получить историю размещения приложения (`get-console-api-v-2-applications-application-id-schedulings`)
- `GET /console/api/v2/applications/{ApplicationId}/available-spaces` - Получение пространств для переноса приложения (`get-console-api-v-2-applications-application-id-available-spaces`)
- `POST /console/api/v2/applications/{ApplicationId}/change-space` - Перенос приложения в другое пространство (`post-console-api-v-2-applications-application-id-change-space`)

## Проекты

- `GET /console/api/v2/projects` - Получить список проектов (`get-console-api-v-2-projects`)
- `POST /console/api/v2/projects` - Создать новый проект из сборки (`post-console-api-v-2-projects`)
- `GET /console/api/v2/projects/{ProjectId}` - Узнать о проекте (`get-console-api-v-2-projects-project-id`)
- `DELETE /console/api/v2/projects/{ProjectId}` - Удалить проект (`delete-console-api-v-2-projects-project-id`)
- `GET /console/api/v2/projects/{ProjectId}/assemblies` - Получить все сборки проекта (`get-console-api-v-2-projects-project-id-assemblies`)
- `POST /console/api/v2/projects/{ProjectId}/assemblies` - Загрузить сборку проекта из файла (`post-console-api-v-2-projects-project-id-assemblies`)
- `GET /console/api/v2/projects/{ProjectId}/assemblies/{Version}` - Узнать подробнее о сборке проекта (`get-console-api-v-2-assemblies-version`)
- `DELETE /console/api/v2/projects/{ProjectId}/assemblies/{Version}` - Удалить сборку проекта (`delete-console-api-v-2-assemblies-version`)
- `GET /console/api/v2/projects/{ProjectId}/versions` DEPRECATED - (DEPRECATED) Получить список сборок проекта (`get-console-api-v-2-projects-versions`)
- `GET /console/api/v2/projects/{ProjectId}/versions/{VersionId}` DEPRECATED - (DEPRECATED) Узнать о сборке проекта (`get-console-api-v-2-versions-version`)
- `DELETE /console/api/v2/projects/{ProjectId}/versions/{VersionId}` DEPRECATED - (DEPRECATED) Удалить сборку проекта (`delete-console-api-v-2-versions-version`)

## Пространства

- `GET /console/api/v2/spaces` - Получить список пространств (`get-console-api-v-2-spaces`)
- `POST /console/api/v2/spaces` - Создать пространство (`post-console-api-v-2-spaces`)
- `GET /console/api/v2/spaces/{SpaceId}` - Узнать о пространстве (`get-console-api-v-2-spaces-space-id`)
- `GET /console/api/v2/spaces/{SpaceId}/applications` - Получить список приложений пространства (`get-console-api-v-2-spaces-space-id-applications`)
- `GET /console/api/v2/spaces/{SpaceId}/user-lists` - Получить списки пользователей пространства (`get-console-api-v-2-spaces-space-id-user-lists`)
- `GET /console/api/v2/spaces/{SpaceId}/projects` - Получить список проектов пространства (`get-console-api-v-2-spaces-space-id-projects`)
- `GET /console/api/v2/spaces/{SpaceId}/participants` - Получить список участников пространства (`get-console-api-v-2-spaces-space-id-participants`)
- `POST /console/api/v2/spaces/{SpaceId}/participants` - Создать новый проект в пространстве (`post-console-api-v-2-spaces-space-id-projects`)

## Профиль пользователя

- `GET /console/api/v2/me` - Получения профиля пользователя (`get-console-api-v-2-me`)

## Сервисы

- `GET /console/api/v2/cloud-services` - Получить список сервисов (`get-cloud-services`)
- `POST /console/api/v2/cloud-services` - Создать сервис (`post-cloud-services`)
- `GET /console/api/v2/cloud-services/{ServiceId}` - Получить сервис (`get-cloud-services-service-id`)
- `GET /console/api/v2/cloud-services/paas` - Получить сервис PaaS (`get-cloud-services-paas`)
- `GET /console/api/v2/cloud-services/{ServiceId}/subscribers` - Получить список абонентов (`get-cloud-services-service-id-subscribers`)
- `POST /console/api/v2/cloud-services/{ServiceId}/subscribers` - Создать абонента (`post-cloud-services-service-id-subscribers`)
- `GET /console/api/v2/cloud-services/{ServiceId}/subscribers/{SubscriberId}` - Получить абонента (`get-cloud-services-service-id-subscribers-subscriber-id`)
- `GET /console/api/v2/cloud-services/{ServiceId}/subscribers/{SubscriberId}/members` - Получить список пользователей абонента (`get-cloud-services-service-id-subscribers-subscriber-id-members`)
- `POST /console/api/v2/cloud-services/{ServiceId}/subscribers/{SubscriberId}/members` - Подключить пользователя к абоненту (`post-cloud-services-service-id-subscribers-subscriber-id-members`)
- `DELETE /console/api/v2/cloud-services/{ServiceId}/subscribers/{SubscriberId}/members` - Отключить пользователя от абонента (`delete-cloud-services-service-id-subscribers-subscriber-id-members`)
- `GET /console/api/v2/cloud-services/{ServiceId}/subscribers/{SubscriberId}/applications` - Получить список приложений пространств абонента (`get-cloud-services-service-id-subscribers-subscriber-id-applications`)
- `GET /console/api/v2/cloud-services/{ServiceId}/subscribers/{SubscriberId}/spaces` - Получить все пространства абонента (`get-cloud-services-service-id-subscribers-subscriber-id-spaces`)

## СУБД

- `GET /console/api/v2/dbms/types` - Получение доступных типов СУБД (`get-console-api-v-2-dbms-types`)
