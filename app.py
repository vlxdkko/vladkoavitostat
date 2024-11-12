from flask import Flask, render_template, request, send_file, abort
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

# Путь к директории, где хранятся файлы каждого пользователя
USER_DATA_FOLDER = 'user_data'


@app.route('/')
def index():
    user_id = request.args.get('user_id')

    if not user_id:
        return "User ID не найден в запросе.", 400

    # Путь к файлу пользователя
    user_file = os.path.join(USER_DATA_FOLDER, f"{user_id}.xlsx")

    if not os.path.exists(user_file):
        return "Файл данных для данного пользователя не найден.", 404

    # Чтение Excel файла пользователя
    df = pd.read_excel(user_file)

    # Используем первый столбец для списка категорий
    categories = df.iloc[:, 0].tolist()

    return render_template('index.html', categories=categories)


@app.route('/upload', methods=['POST'])
def upload():
    user_id = request.args.get('user_id')

    if not user_id:
        return "User ID не найден в запросе.", 400

    # Путь к файлу пользователя
    user_file = os.path.join(USER_DATA_FOLDER, f"{user_id}.xlsx")

    if not os.path.exists(user_file):
        return "Файл данных для данного пользователя не найден.", 404

    selected_categories = request.form.getlist('categories')  # Получаем выбранные категории

    # Чтение Excel файла пользователя
    df = pd.read_excel(user_file)

    # Проверка, достаточно ли столбцов для построения графика
    if len(df.columns) < 3:
        return "Недостаточно данных для построения графика (меньше трех столбцов)", 400

    # Используем первый столбец для категорий
    categories = df.iloc[:, 0]
    days = pd.to_datetime(df.columns[2:]).strftime('%m-%d')
    views = df.iloc[:, 2:]
    views.columns = days
    views = views.T.groupby(level=0).sum().T

    # Фильтруем данные на основе выбранных категорий
    selected_data = views[categories.isin(selected_categories)]

    # Построение графика
    plt.figure(figsize=(10, 5))
    for index, category in selected_data.iterrows():
        plt.plot(selected_data.columns, category, label=categories.iloc[index])

    plt.title("Просмотры по выбранным категориям")
    plt.xlabel("Дни")
    plt.ylabel("Количество просмотров")
    plt.legend()

    # Сохранение графика в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()  # Очистка графика после сохранения

    return send_file(buf, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
