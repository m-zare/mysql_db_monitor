import datetime
import yaml
from flask import (
    Flask, 
    render_template,
)

from mysql.connector import (
    Error, 
    connect, 
    MySQLConnection
)


# from turbo_flask import Turbo
def create_app():
    app = Flask(__name__)

    @app.route("/healthcheck")
    def health_database_status():
        dbs = read_yml("db_configs.yml")
        response = []
        for item in dbs:
            connection = MySQLConnection()
            result = ""
            msg = {"Database": item["database"], "Hostname": item['host']}
            try:
                connection = connect(
                    host=item["host"],
                    database=item["database"],
                    user=item["username"],
                    password=item["password"],
                )
                if connection.is_connected():
                    db_Info = connection.get_server_info()
                    result = "Connected to MySQL Server version {}".format(db_Info)
                    cursor = connection.cursor()
                    cursor.execute("select database();")
                    record = cursor.fetchone()
                    result = "{}\nYou're connected to database: {}\n".format(
                        result, record
                    )
                msg["Status"] = "OK"
            except Error as e:
                result = "{}Error while connecting to MySQL {}\n".format(result, e)
                msg["Error"] = e.msg
                msg["Status"] = "Error"
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
                    result = "{}MySQL connection is closed".format(result)
            msg["Time"] = datetime.datetime.now().ctime()
            msg["Message"] = result
            response.append(msg)
        return response

    @app.route("/")
    def index():
        response = health_database_status()
        return render_template("index.html", data=response)

    return app


def read_yml(path: str):
    with open(path) as file:
        return yaml.load(file, Loader=yaml.FullLoader)
