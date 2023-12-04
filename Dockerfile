# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Install Python packages
RUN pip3 install matplotlib pandas numpy yfinance mplfinance scikit-learn pyppeteer bs4 diagrams
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

CMD ["python3"]

