import os
from flask import Flask, render_template, request, send_from_directory
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  
app = Flask(__name__)
UPLOAD_FOLDER = 'static/compressed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_file_size(file_path):
    return round(os.path.getsize(file_path) / 1024, 2)  # KB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
@app.route('/compress', methods=['POST'])
def compress():
    img_type = request.form['img_type']
    compression_level = request.form['compression_level']
    uploaded_file = request.files['image']

    if uploaded_file.filename == '':
        return 'No file uploaded', 400

    img = Image.open(uploaded_file)
    original_filename = uploaded_file.filename
    base_filename = original_filename.rsplit('.', 1)[0]
    extension = img_type.lower()

   
    if extension in ['jpg', 'jpeg']:
        if img.mode == 'RGBA':
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  
            img = background
        else:
            img = img.convert('RGB')

    
    temp_original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_filename}_original.{extension}")
    img.save(temp_original_path)
    original_size = get_file_size(temp_original_path)

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_filename}_compressed.{extension}")

    if extension in ['jpg', 'jpeg']:
        if compression_level == 'high':
            quality = 85
        elif compression_level == 'medium':
            quality = 60
        else:  
            quality = 30

        img.save(save_path, optimize=True, quality=quality)

    elif extension == 'png':
        if compression_level == 'high':
            compress_level = 1
        elif compression_level == 'medium':
            compress_level = 5
        else:
            compress_level = 9

        img.save(save_path, optimize=True, compress_level=compress_level)

    else:
        img.save(save_path)

    compressed_size = get_file_size(save_path)

    return render_template(
        'index.html',
        original_size=original_size,
        compressed_size=compressed_size,
        download_link=save_path.replace('\\', '/')
    )


@app.route('/download/<path:filename>')
def download(filename):
    directory = os.path.dirname(filename)
    file = os.path.basename(filename)
    return send_from_directory(directory, file, as_attachment=True)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
