# *** Base ***
FROM python:3.10.4-slim

# Copy script
ADD anastasia /anastasia
ADD README.md /

# Install Anastasia
ADD pyproject.toml /pyproject.toml
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Run script
ENTRYPOINT [ "python3", "-m", "anastasia" ]

HEALTHCHECK CMD curl --fail http://localhost:8080 || exit 1 
