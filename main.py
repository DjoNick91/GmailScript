import base64
import os.path

from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]


def login():
    # Авторизация, перед использование сервиса
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("gmail", "v1", credentials=creds)
    except HttpError as error:
        print(f"An error occurred: {error}")
    return service


def get_messages(service):
    # Получить 5 последних сообщений
    results = service.users().messages().list(userId="me", maxResults=5).execute()
    for r in results['messages']:
        id = r['id']
        messages = service.users().messages().get(userId='me', id=id).execute()
        print(messages['id'])
        headers = messages['payload']['headers']
        otvet = {}
        for h in headers:
            if h['name'] == 'Subject':
                subject = h['value']
                otvet['Тема'] = subject
            if h['name'] == 'From':
                sender = h['value']
                otvet['Отправитель'] = sender
            if h['name'] == 'Date':
                date = h['value']
                otvet['Дата'] = date
        print(otvet)
        pass


def sent_message(service):
    # Отправляет тестовое сообщение самому себе
    message = EmailMessage()
    message.set_content("Это тестовое письмо самому себе")
    message["To"] = (service.users().getProfile(userId='me').execute())['emailAddress']
    message["From"] = "me"
    message["Subject"] = "Тестовое письмо"
    message["Body"] = "Тестовое письмо"
    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Сообщение отправлено. Message id: {send_message["id"]}')
    pass


def delete_message(service):
    # Перемещает сообщение с указанным ID в корзину
    message_id = input('Введите id сообщения, которое нужно удалить: ')
    try:
        service.users().messages().trash(userId='me', id=message_id).execute()
    except Exception:
        print("Сообщения с указаным id не существует")


if __name__ == "__main__":
    print(f'Данный скрипт позволяет:\n'
          f'1. Получить 5 последних сообщений\n'
          f'2. Отправить тестовое соообщение самому себе\n'
          f'3. Удалить сообщение по идентификатору')
    choise = input('Выберите действие: ')
    if choise == '1':
        get_messages(login())
    if choise == '2':
        sent_message(login())
    if choise == '3':
        delete_message(login())
    else:
        print('Вы ввели не корректный номер')
