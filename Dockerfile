FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
RUN mkdir ~/.streamlit
WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["live_data.py"]
