FROM python:3.13-alpine
WORKDIR /pizzaonehitai
COPY *.py requirements.txt /pizzaonehitai/
COPY ./riot /pizzaonehitai/riot
#COPY ./plugins /pizzaonehitai/plugins
COPY ./assets /pizzaonehitai/assets
#COPY ./config /pizzaonehitai/config
# COPY ./assets/gif /pizzaonehitai/assets/gif
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY --from=golang:latest /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:${PATH}"

COPY ./plugins/gifgenerator_go /pizzaonehitai/plugins/gifgenerator_go
WORKDIR /pizzaonehitai/plugins/gifgenerator_go

RUN go mod tidy
RUN go build

WORKDIR /pizzaonehitai

CMD ["python","-u","main.py"]