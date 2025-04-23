FROM python:3.10-slim

# تثبيت المتطلبات الأساسية
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# تثبيت Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# تثبيت Chromedriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') \
    && CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}) \
    && wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm chromedriver_linux64.zip

# إعداد بيئة العمل
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# تعيين متغيرات البيئة
ENV GOOGLE_CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# تشغيل التطبيق
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "server:app", "--bind", "0.0.0.0:$PORT"]
