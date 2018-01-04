# Build:
#   docker build -t address-processor .
# Run:
#   docker run -e address-processor
#   kubectl run address-processor --image=gcr.io/voterdb-test/address-processor

FROM python:2.7

WORKDIR /usr/src/app

COPY . .

RUN python -m pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./AddressProcessor.py"]
