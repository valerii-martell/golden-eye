FROM python:3.10

RUN useradd --create-home goldeneye
WORKDIR /golden_eye
ENV PORT 5000

COPY ./ .
RUN pip install -r requirements.txt
RUN chown -R goldeneye:goldeneye ./
USER goldeneye

EXPOSE 5000
CMD gunicorn -w 4 --bind 0.0.0.0:$PORT app:app