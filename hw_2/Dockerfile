FROM python:3.8

COPY ./src hw_2/src
WORKDIR "/hw_2"

RUN apt-get update
RUN apt-get install -y graphviz
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pydot

RUN python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple fibs-ast-drawer-by-dameron78==0.0.3
RUN python3 src/main.py

RUN apt-get install -y texlive-latex-base
RUN apt-get install -y texlive-lang-cyrillic

RUN pdflatex -output-directory artifacts artifacts/output.tex