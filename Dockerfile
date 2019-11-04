FROM python:latest

RUN pip3 install pillow

COPY imgresize.py /imgresize.py

CMD python3 imgresize.py
