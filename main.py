# main.py

from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
import os
import uuid
import urllib.parse
import logging
import traceback

from image_processing import VisaPhotoProcessor
from utils import allowed_file, is_allowed_file, clean_filename, ALLOWED_EXTENSIONS

# Инициализация Flask-приложения
app = Flask(__name__, static_folder='static', template_folder='templates')

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Конфигурация директорий
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')
PREVIEW_FOLDER = os.path.join(BASE_DIR, 'previews')
FONTS_FOLDER = os.path.join(BASE_DIR, 'fonts')

# Создание необходимых папок
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, PREVIEW_FOLDER, FONTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)
    logging.info(f"Created directory: {folder}")

# Настройка конфигурации приложения
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Ограничение на 10 МБ

@app.route('/')
def index():
    """
    Главная страница.
    """
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static_files(path):
    """
    Отправка статических файлов.
    """
    return send_from_directory('static', path)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Обработка загрузки файла.
    """
    input_path = None
    processed_path = None
    preview_path = None
    printable_path = None
    printable_preview_path = None

    try:
        if 'file' not in request.files:
            logging.warning("No file part in the request")
            return jsonify({'error': 'Нет файла в запросе'}), 400

        file = request.files['file']
        if file.filename == '':
            logging.warning("No selected file")
            return jsonify({'error': 'Файл не выбран'}), 400

        if file and allowed_file(file.filename):
            base_filename = clean_filename(file.filename)
            unique_id = str(uuid.uuid4())

            unique_filename = f"{unique_id}_{base_filename}"
            processed_filename = f"processed_{unique_id}_{base_filename}"
            preview_filename = f"preview_processed_{unique_id}_{base_filename}"
            printable_filename = f"printable_{unique_id}_{base_filename}"
            printable_preview_filename = f"preview_printable_{unique_id}_{base_filename}"

            input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
            preview_path = os.path.join(PREVIEW_FOLDER, preview_filename)
            printable_path = os.path.join(PROCESSED_FOLDER, printable_filename)
            printable_preview_path = os.path.join(PREVIEW_FOLDER, printable_preview_filename)

            file.save(input_path)
            logging.info(f"File saved at {input_path}")

            if os.path.getsize(input_path) > 10 * 1024 * 1024:
                raise ValueError("Размер файла превышает 10 МБ")

            # Используем класс VisaPhotoProcessor для обработки изображения
            processor = VisaPhotoProcessor(
                input_path=input_path,
                processed_path=processed_path,
                preview_path=preview_path,
                printable_path=printable_path,
                printable_preview_path=printable_preview_path,
                fonts_folder=FONTS_FOLDER
            )

            # Обработка изображения
            photo_info = processor.process()

            response_data = {
                'success': True,
                'preview_filename': os.path.basename(preview_path),
                'download_filename': os.path.basename(processed_path),
                'printable_filename': os.path.basename(printable_path),
                'printable_preview_filename': os.path.basename(printable_preview_path),
                'photo_info': photo_info,
                'message': 'Файл успешно обработан'
            }

            logging.info("File processed successfully")

            # Удаляем загруженный файл после обработки
            if input_path and os.path.exists(input_path):
                os.remove(input_path)
                logging.info(f"Cleaned up input file: {input_path}")

            return jsonify(response_data)

        else:
            logging.warning("Invalid file type uploaded")
            return jsonify({
                'error': 'Недопустимый тип файла',
                'message': 'Поддерживаемые форматы: JPG, JPEG, PNG'
            }), 400

    except Exception as e:
        logging.error(f"Error during file upload: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")

        # Удаление файлов в случае ошибки
        for path in [input_path, processed_path, preview_path, printable_path, printable_preview_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logging.info(f"Removed file: {path}")
                except Exception as cleanup_error:
                    logging.error(f"Error cleaning up file {path}: {cleanup_error}")

        return jsonify({
            'error': 'Ошибка при обработке изображения',
            'message': str(e)
        }), 500

@app.route('/previews/<filename>')
def get_preview(filename):
    """
    Получение превью.
    """
    try:
        # Декодирование URL и очистка имени файла
        decoded_filename = urllib.parse.unquote(filename)
        clean_filename_var = clean_filename(decoded_filename)
        preview_path = os.path.join(PREVIEW_FOLDER, clean_filename_var)

        # Проверка существования файла
        if not os.path.exists(preview_path):
            logging.warning(f"Preview not found: {filename}")
            return jsonify({'error': 'Превью не найдено'}), 404

        # Проверка расширения файла для безопасности
        if not is_allowed_file(preview_path):
            logging.warning(f"Attempt to access disallowed file type: {filename}")
            return jsonify({'error': 'Недопустимый тип файла'}), 400

        logging.info(f"Serving preview: {preview_path}")
        return send_file(preview_path, mimetype='image/jpeg', max_age=300)
    except Exception as e:
        logging.error(f"Preview error: {str(e)}")
        return jsonify({'error': 'Произошла ошибка при получении превью'}), 500

@app.route('/previews/printable/<filename>')
def get_printable_preview(filename):
    """
    Получение превью для изображения для печати.
    """
    try:
        # Декодирование URL и очистка имени файла
        decoded_filename = urllib.parse.unquote(filename)
        clean_filename_var = clean_filename(decoded_filename)
        preview_path = os.path.join(PREVIEW_FOLDER, clean_filename_var)

        # Проверка существования файла
        if not os.path.exists(preview_path):
            logging.warning(f"Printable preview not found: {filename}")
            return jsonify({'error': 'Превью не найдено'}), 404

        # Проверка расширения файла для безопасности
        if not is_allowed_file(preview_path):
            logging.warning(f"Attempt to access disallowed file type: {filename}")
            return jsonify({'error': 'Недопустимый тип файла'}), 400

        logging.info(f"Serving printable preview: {preview_path}")
        return send_file(preview_path, mimetype='image/jpeg', max_age=300)
    except Exception as e:
        logging.error(f"Printable preview error: {str(e)}")
        return jsonify({'error': 'Произошла ошибка при получении превью для печати'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """
    Загрузка обработанного файла.
    """
    try:
        # Декодирование URL и очистка имени файла
        decoded_filename = urllib.parse.unquote(filename)
        clean_filename_var = clean_filename(decoded_filename)
        file_path = os.path.join(PROCESSED_FOLDER, clean_filename_var)

        # Проверка существования файла
        if not os.path.exists(file_path):
            logging.warning(f"Processed file not found: {filename}")
            return jsonify({'error': 'Файл не найден'}), 404

        # Проверка расширения файла для безопасности
        if not is_allowed_file(file_path):
            logging.warning(f"Attempt to download disallowed file type: {filename}")
            return jsonify({'error': 'Недопустимый тип файла'}), 400

        response = send_file(
            file_path,
            as_attachment=True,
            download_name="visa_photo.jpg",
            mimetype='image/jpeg'
        )

        # Отключение кеширования
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        logging.info(f"Serving download: {file_path}")
        return response
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Произошла ошибка при загрузке файла'}), 500

@app.route('/download_printable/<filename>')
def download_printable(filename):
    """
    Загрузка изображения для печати 4x6".
    """
    try:
        # Декодирование URL и очистка имени файла
        decoded_filename = urllib.parse.unquote(filename)
        clean_filename_var = clean_filename(decoded_filename)
        file_path = os.path.join(PROCESSED_FOLDER, clean_filename_var)

        # Проверка существования файла
        if not os.path.exists(file_path):
            logging.warning(f"Printable file not found: {filename}")
            return jsonify({'error': 'Файл не найден'}), 404

        # Проверка расширения файла для безопасности
        if not is_allowed_file(file_path):
            logging.warning(f"Attempt to download disallowed file type: {filename}")
            return jsonify({'error': 'Недопустимый тип файла'}), 400

        response = send_file(
            file_path,
            as_attachment=True,
            download_name="printable_photo.jpg",
            mimetype='image/jpeg'
        )

        # Отключение кеширования
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        logging.info(f"Serving printable download: {file_path}")
        return response
    except Exception as e:
        logging.error(f"Download printable error: {str(e)}")
        return jsonify({'error': 'Произошла ошибка при загрузке файла для печати'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)