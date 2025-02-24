FROM python:3.13-alpine
WORKDIR /pizzaonehitai
COPY *.py requirements.txt /pizzaonehitai/
COPY ./riot /pizzaonehitai/riot
#COPY ./plugins /pizzaonehitai/plugins
COPY ./assets /pizzaonehitai/assets
COPY ./assets/gif /pizzaonehitai/assets/gif
RUN pip install -r requirements.txt
CMD ["python","-u","main.py"]