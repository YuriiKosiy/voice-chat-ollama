# Voice Chat with Ollama and Amazon Polly (Python)

Цей проект дозволяє вести голосовий діалог з використанням моделі Llama3.1:8b через Ollama та синтезу мовлення за допомогою Amazon Polly.

## Встановлення

### 1. Встановлення Ollama

Перш за все, потрібно встановити Ollama для доступу до моделі Llama3 (<a href="https://ollama.com/download" target="_blank">https://ollama.com/download</a>)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Встановлюємо та запускаємо потрібну модель з сайту Ollama <a href="https://ollama.com/library" target="_blank">https://ollama.com/library</a>:
```bash
ollama run llama3.1
```
Встановлюємо підтримку ollama в python6
```bash
pip install ollama
```
Для перевірки чи запуску Ollama як сервіс:
```bash
ollama serve
```

### 2. Встановлення AWS CLI

Після цього потрібно встановити AWS CLI для доступу до сервісу Amazon Polly. (для Ubuntu подібних ОС, я користуюсь Linux Mint)

``` bash
sudo apt update
sudo apt install awscli
```
### 3. Налаштування AWS CLI

Після встановлення AWS CLI потрібно налаштувати облікові дані для доступу до сервісів AWS.

```bash
aws configure
```
Введіть свої AWS Access Key ID, AWS Secret Access Key, регіон та формат виводу.

### 4. Встановлення додаткових залежностей

Переконайтесь, що у вас встановлені наступні бібліотеки:

```bash
pip install boto3 speechrecognition pyaudio mpg321
```
'pyaudio' потрібен для роботи з мікрофоном, 'speechrecognition' для розпізнавання голосу, а 'mpg321' для відтворення звукових файлів.

## Використання

## Основні блоки коду

### 1. Ініціалізація клієнта Amazon Polly

Цей блок ініціалізує клієнт Amazon Polly, який буде використовуватися для синтезу мовлення.
```bash
polly = boto3.client('polly', region_name='us-west-2')
```

### 2. Функція для надсилання запиту до моделі Llama
Ця функція надсилає поточну повідомленя до моделі Llama і отримує відповідь. Також, по ідеї, така реалізація дозволяє "пам'ятати" контекст, але це не точно:
```python
async def ask_llama(client, messages):
    response_stream = await client.chat(model="llama3.1:8b", messages=messages, stream=True)
    accumulated_text = ""
    async for part in response_stream:
        content = part["message"]["content"]
        accumulated_text += content

        if any(content.endswith(end) for end in [".", "!", "?"]):
            print(accumulated_text, end="", flush=True)
            await speak_response(accumulated_text)
            accumulated_text = ""
```
model - перевіряємо встановлення моделі ollama командою:
```bash
ollama list
```
### 3. Функція для розпізнавання голосу
Ця функція захоплює голос користувача через мікрофон і перетворює його в текст.
```python
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Слухаю ваш запит...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio, language="uk-UA")
            print(f"Ви сказали: {query}")
            return query
        except sr.UnknownValueError:
            print("Не вдалося розпізнати голос.")
            return None
        except sr.RequestError:
            print("Помилка з'єднання зі службою розпізнавання.")
            return None
```
Не знаю нашо там 'language="uk-UA"' адже і англійською все більш як чудово

### 4. Функція для синтезу мови
Ця функція використовує Amazon Polly для озвучення текстової відповіді, використовуючи формат SSML для налаштування параметрів голосу.
```python
async def speak_response(response):
    ssml_text = f"""
    <speak>
        <prosody rate="medium" pitch="medium" volume="medium">
            {response}
        </prosody>
    </speak>
    """
    result = polly.synthesize_speech(
        TextType='ssml',
        Text=ssml_text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
    with open('response.mp3', 'wb') as file:
        file.write(result['AudioStream'].read())
    os.system("mpg321 response.mp3")
```
Доступні голоси тут <a href="https://docs.aws.amazon.com/polly/latest/dg/available-voices.html" target="_blank">Available voices</a>
Для англомовних запитів чудово працює **Joanna**, для україномовних, на жаль, нема в Амазона варіантів, тествував з **Tatyana**, то дуже сильний російський акцент.

### 5. Основний цикл програми
Основний цикл програми, який працює в режимі діалогу, зберігаючи контекст розмови і постійно взаємодіючи з користувачем.

```python
async def main():
    client = AsyncClient()  # Ініціалізуємо клієнта один раз
    messages = []  # Ініціалізуємо історію діалогу

    while True:
        question = recognize_speech()
        if question:
            messages.append({"role": "user", "content": question})
            await ask_llama(client, messages)
```

## Запуск

Після виконання всіх налаштувань, можна запустити програму:
```bash
python3 chat.py
```
**Якщо виводить лишнє інфо після запуску команди, наприклад, помилки ALSA (які в принципі не впливають на роботу) то можемо запустити програму так**
```bash
python3 chat.py 2>/dev/null
```
- чистіший вивід буде

# Примітки

* **Контекст діалогу:** Програма зберігає історію повідомлень для забезпечення безперервного діалогу.
* **Amazon Polly:** Використовується для синтезу мови. Використовуйте відповідні облікові дані AWS для доступу до сервісу.

## Це не є професійна програма та створенна тільки як ознайомлення з можливостями розпізнавання голосу та синтезу мови. Я не є програмістом і мій код може містити помилки, неточності або взагалі бути не актуальним...


