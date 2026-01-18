from flask import Flask, render_template, request, jsonify
import os
import random

app = Flask(__name__)

# Folder database lagu
LAGU_FOLDER = 'database_lagu'

def baca_lagu_dari_file(genre, asal):
    """
    Membaca daftar lagu dari file .txt
    """
    filepath = os.path.join(LAGU_FOLDER, genre, f'{asal}.txt')
    
    if not os.path.exists(filepath):
        return []
    
    lagu_list = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Format: Judul Lagu | Artis | Tahun
                    parts = line.split('|')
                    if len(parts) == 3:
                        lagu_list.append({
                            'judul': parts[0].strip(),
                            'artis': parts[1].strip(),
                            'tahun': parts[2].strip()
                        })
    except Exception as e:
        print(f"Error membaca file {filepath}: {e}")
    
    return lagu_list

def algoritma_rekomendasi(lagu_list, genre, asal, preferensi=""):
    """
    Algoritma sederhana untuk memberikan rekomendasi
    (Simulasi AI tanpa perlu API key)
    """
    if not lagu_list:
        return {
            "error": "Tidak ada lagu yang ditemukan untuk genre dan asal ini."
        }
    
    random.shuffle(lagu_list)
    
    preferensi_lower = preferensi.lower()
    keywords = {
        'tahun': ['tahun', 'old', 'lawas', 'jadul', 'klasik', '90', '80', '2000'],
        'tempo': ['lambat', 'slow', 'pelan', 'cepat', 'fast', 'upbeat'],
        'populer': ['populer', 'terkenal', 'hits', 'famous', 'viral']
    }
    
    scored_songs = []
    for lagu in lagu_list:
        score = 5
        
        # Boost score berdasarkan preferensi tahun
        if any(kw in preferensi_lower for kw in keywords['tahun']):
            tahun = int(lagu['tahun'])
            if '90' in preferensi_lower or '1990' in preferensi_lower:
                if 1990 <= tahun < 2000:
                    score += 3
            elif '80' in preferensi_lower or '1980' in preferensi_lower:
                if 1980 <= tahun < 1990:
                    score += 3
            elif '2000' in preferensi_lower:
                if 2000 <= tahun < 2010:
                    score += 3
            elif 'lawas' in preferensi_lower or 'klasik' in preferensi_lower:
                if tahun < 2000:
                    score += 2
        
        if any(kw in preferensi_lower for kw in keywords['populer']):
            tahun = int(lagu['tahun'])
            if 2010 <= tahun <= 2020:
                score += 2
        
        scored_songs.append((lagu, score))
    
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    top_songs = [song for song, score in scored_songs[:5]]
    
    # Buat penjelasan rekomendasi
    genre_desc = {
        'sedih': 'menyentuh hati dan penuh emosi',
        'senang': 'ceria dan menghibur',
        'romantis': 'penuh cinta dan perasaan',
        'semangat': 'memotivasi dan membangkitkan semangat'
    }
    
    asal_desc = {
        'lokal': 'Indonesia',
        'barat': 'barat/internasional'
    }
    
    rekomendasi_text = f"Berdasarkan pencarian kamu untuk lagu {genre} dari {asal_desc.get(asal, asal)}"
    
    if preferensi:
        rekomendasi_text += f" dengan preferensi '{preferensi}'"
    
    rekomendasi_text += f", berikut adalah rekomendasi terbaik:\n\n"
    
    for i, lagu in enumerate(top_songs, 1):
        rekomendasi_text += f"{i}. **{lagu['judul']}** - {lagu['artis']} ({lagu['tahun']})\n"
        
        # Alasan rekomendasi
        if i == 1:
            rekomendasi_text += f"   → Lagu ini sangat cocok karena {genre_desc.get(genre, genre)} dan menjadi favorit banyak orang.\n\n"
        elif i == 2:
            rekomendasi_text += f"   → Rekomendasi kedua ini memiliki karakteristik yang sesuai dengan mood {genre} yang kamu cari.\n\n"
        elif i == 3:
            rekomendasi_text += f"   → Pilihan alternatif yang tidak kalah bagus untuk menemani hari kamu.\n\n"
        else:
            rekomendasi_text += f"   → Lagu ini juga layak untuk kamu dengarkan.\n\n"
    
    rekomendasi_text += f"\n💡 Tips: Semua lagu di atas dipilih khusus untuk mood {genre} kamu!"
    
    return {
        "recommendation": rekomendasi_text,
        "top_songs": top_songs,
        "all_songs": lagu_list
    }

@app.route('/')
def index():
    # Baca genre yang tersedia dari folder
    genres = []
    if os.path.exists(LAGU_FOLDER):
        genres = [d for d in os.listdir(LAGU_FOLDER) 
                 if os.path.isdir(os.path.join(LAGU_FOLDER, d))]
    return render_template('index.html', genres=genres)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    mood = data.get('mood', '').lower()
    origin = data.get('origin', '').lower()
    preference = data.get('preference', '')
    
    # Baca lagu dari file
    lagu_list = baca_lagu_dari_file(mood, origin)
    
    result = algoritma_rekomendasi(lagu_list, mood, origin, preference)
    
    return jsonify(result)

@app.route('/api/genres')
def get_genres():
    genres = []
    if os.path.exists(LAGU_FOLDER):
        genres = [d for d in os.listdir(LAGU_FOLDER) 
                 if os.path.isdir(os.path.join(LAGU_FOLDER, d))]
    return jsonify(genres)

if __name__ == '__main__':
    # Buat cek folder aja (kalau lupa)
    if not os.path.exists(LAGU_FOLDER):
        print(f"Folder '{LAGU_FOLDER}' tidak ditemukan!")
    
    app.run(debug=True)