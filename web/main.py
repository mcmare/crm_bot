import os
import sqlite3
import uuid
import json
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = '../db.sqlite3'
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Создаем папку для загрузок, если ее нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/zn-<zn_number>', methods=['GET', 'POST'])
def order_detail(zn_number):
    tab = request.args.get('tab', 'info')  # Получаем активную вкладку из параметра URL

    conn = get_db_connection()
    order_work = conn.execute(
        'SELECT * FROM orders_work WHERE n_order_work = ?',
        (zn_number,)
    ).fetchone()

    if not order_work:
        conn.close()
        abort(404)

    # Обработка смены статуса
    if request.method == 'POST' and 'action' in request.form:
        action = request.form.get('action')
        if action == 'take' and order_work['status'] == 1:
            conn.execute(
                'UPDATE orders_work SET status = 2 WHERE n_order_work = ?',
                (zn_number,)
            )
        elif action == 'complete' and order_work['status'] == 2:
            conn.execute(
                'UPDATE orders_work SET status = 3 WHERE n_order_work = ?',
                (zn_number,)
            )
        conn.commit()
        order_work = conn.execute(
            'SELECT * FROM orders_work WHERE n_order_work = ?',
            (zn_number,)
        ).fetchone()

    # Получаем связанные данные
    order = conn.execute(
        'SELECT * FROM orders WHERE id_order = ?',
        (order_work['n_order'],)
    ).fetchone()

    responsible = conn.execute(
        'SELECT * FROM users WHERE id = ?',
        (order_work['responsible'],)
    ).fetchone() if order_work['responsible'] else None

    # Парсим список работ
    works_list = []
    total_sum = 0
    if order_work['list_works']:
        works_data = json.loads(order_work['list_works'])
        for work in works_data:
            for work_id, quantity in work.items():
                work_info = conn.execute(
                    'SELECT * FROM list_works WHERE id = ?',
                    (work_id,)
                ).fetchone()
                if work_info:
                    works_list.append({
                        'id': work_id,
                        'name': work_info['name'],
                        'price': work_info['price'],
                        'quantity': quantity
                    })
                    total_sum += work_info['price'] * quantity

    # Получаем фотографии
    photos = []
    if order_work['photos']:
        photo_ids = json.loads(order_work['photos'])
        for photo_id in photo_ids:
            photo = conn.execute(
                'SELECT * FROM photos WHERE id_photo = ?',
                (photo_id,)
            ).fetchone()
            if photo:
                photos.append(photo['url'])

    # Получаем все доступные работы для выпадающего списка
    all_works = conn.execute('SELECT * FROM list_works').fetchall()

    conn.close()

    statuses = {
        1: 'Новый',
        2: 'В работе',
        3: 'Завершен',
        4: 'Принят',
        5: 'Не принят'
    }

    return render_template('order_detail.html',
                           zn_number=zn_number,
                           order=order,
                           order_work=order_work,
                           responsible=responsible,
                           works_list=works_list,
                           photos=photos,
                           statuses=statuses,
                           total_sum=total_sum,
                           all_works=all_works,
                           active_tab=tab)


@app.route('/add_work/<zn_number>', methods=['POST'])
def add_work(zn_number):
    work_id = request.form['work_id']
    quantity = int(request.form['quantity'])

    conn = get_db_connection()
    order_work = conn.execute(
        'SELECT * FROM orders_work WHERE n_order_work = ?',
        (zn_number,)
    ).fetchone()

    if not order_work:
        conn.close()
        abort(404)

    # Получаем текущий список работ
    works_data = []
    if order_work['list_works']:
        works_data = json.loads(order_work['list_works'])

    # Проверяем, есть ли уже такая работа в ЗН
    work_exists = False
    for work in works_data:
        if work_id in work:
            work[work_id] += quantity
            work_exists = True
            break

    # Если работы еще нет - добавляем новую
    if not work_exists:
        works_data.append({work_id: quantity})

    # Обновляем запись в БД
    conn.execute(
        'UPDATE orders_work SET list_works = ? WHERE n_order_work = ?',
        (json.dumps(works_data), zn_number)
    )

    conn.commit()
    conn.close()
    return redirect(url_for('order_detail', zn_number=zn_number, tab='works'))


@app.route('/update_work/<zn_number>/<work_id>', methods=['POST'])
def update_work(zn_number, work_id):
    new_quantity = int(request.form['quantity'])

    conn = get_db_connection()
    order_work = conn.execute(
        'SELECT * FROM orders_work WHERE n_order_work = ?',
        (zn_number,)
    ).fetchone()

    if not order_work:
        conn.close()
        abort(404)

    # Обновляем количество в списке работ
    if order_work['list_works']:
        works_data = json.loads(order_work['list_works'])
        for work in works_data:
            if work_id in work:
                work[work_id] = new_quantity
                break

        conn.execute(
            'UPDATE orders_work SET list_works = ? WHERE n_order_work = ?',
            (json.dumps(works_data), zn_number)
        )

        conn.commit()

    conn.close()
    return redirect(url_for('order_detail', zn_number=zn_number, tab='works'))


@app.route('/delete_work/<zn_number>/<work_id>', methods=['POST'])
def delete_work(zn_number, work_id):
    conn = get_db_connection()
    order_work = conn.execute(
        'SELECT * FROM orders_work WHERE n_order_work = ?',
        (zn_number,)
    ).fetchone()

    if not order_work:
        conn.close()
        abort(404)

    # Удаляем работу из списка
    if order_work['list_works']:
        works_data = json.loads(order_work['list_works'])
        new_works_data = [work for work in works_data if work_id not in work]

        conn.execute(
            'UPDATE orders_work SET list_works = ? WHERE n_order_work = ?',
            (json.dumps(new_works_data), zn_number)
        )

        conn.commit()

    conn.close()
    return redirect(url_for('order_detail', zn_number=zn_number, tab='works'))


@app.route('/upload_photo/<zn_number>', methods=['POST'])
def upload_photo(zn_number):
    if 'photo' not in request.files:
        return redirect(url_for('order_detail', zn_number=zn_number, tab='photos'))

    files = request.files.getlist('photo')
    conn = get_db_connection()
    order_work = conn.execute(
        'SELECT * FROM orders_work WHERE n_order_work = ?',
        (zn_number,)
    ).fetchone()

    if not order_work:
        conn.close()
        abort(404)

    photo_ids = []
    if order_work['photos']:
        photo_ids = json.loads(order_work['photos'])

    for file in files:
        if file.filename == '':
            continue

        # Генерируем уникальный ID для фото
        photo_uuid = str(uuid.uuid4())
        filename = secure_filename(f"{photo_uuid}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Сохраняем в базу данных
        conn.execute(
            'INSERT INTO photos (id_photo, url) VALUES (?, ?)',
            (photo_uuid, filename)
        )
        photo_ids.append(photo_uuid)

    # Обновляем запись заказ-наряда
    conn.execute(
        'UPDATE orders_work SET photos = ? WHERE n_order_work = ?',
        (json.dumps(photo_ids), zn_number)
    )

    conn.commit()
    conn.close()
    return redirect(url_for('order_detail', zn_number=zn_number, tab='photos'))


@app.route('/delete_photo/<zn_number>/<filename>', methods=['POST'])
def delete_photo(zn_number, filename):
    conn = get_db_connection()
    try:
        # Находим id_photo по имени файла
        photo = conn.execute(
            'SELECT * FROM photos WHERE url = ?',
            (filename,)
        ).fetchone()

        if photo:
            # Удаляем фото из таблицы photos
            conn.execute(
                'DELETE FROM photos WHERE id_photo = ?',
                (photo['id_photo'],)
            )

            # Удаляем ссылку на фото из orders_work
            order_work = conn.execute(
                'SELECT * FROM orders_work WHERE n_order_work = ?',
                (zn_number,)
            ).fetchone()

            if order_work and order_work['photos']:
                photo_ids = json.loads(order_work['photos'])
                new_photo_ids = [pid for pid in photo_ids if pid != photo['id_photo']]

                conn.execute(
                    'UPDATE orders_work SET photos = ? WHERE n_order_work = ?',
                    (json.dumps(new_photo_ids), zn_number)
                )

            conn.commit()
    except Exception as e:
        print(f"Error deleting photo: {e}")
    finally:
        conn.close()

    return redirect(url_for('order_detail', zn_number=zn_number, tab='photos'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)