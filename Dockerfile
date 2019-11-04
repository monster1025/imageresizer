FROM python:3.5.8-alpine

RUN pip3 install pillow

COPY imgresize.py /imgresize.py

CMD python3 imgresize.py