FROM python:slim

RUN pip3 install pillow

ADD imgresize.py /imgresize.py

CMD python3 imgresize.py
