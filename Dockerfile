# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Install Python packages
RUN pip install --no-cache-dir matplotlib pandas numpy yfinance mplfinance scikit-learn pyppeteer bs4

CMD ["python3"]

