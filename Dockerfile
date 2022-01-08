# *** Base ***
FROM python:3.9.1-slim

# Install Santa
ADD requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy script
ADD anastasia/ anastasia/

# Run script
ENTRYPOINT ["python3", "-m", "anastasia"]
