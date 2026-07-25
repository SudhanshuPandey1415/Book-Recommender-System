# 📚 BookShelf — Recommender & Reminder System

BookShelf is a premium, visually stunning web application built with **Streamlit** that combines a collaborative-filtering book recommendation system with a smart reading list manager and reminder dispatcher. It features a modern dark-mode glassmorphic interface, smooth animation cascades, and native notification triggers.

---

## ✨ Features

### 1. 🔥 Top Trending Books
* Showcases the popular and highest-rated books across the platform.
* Dynamic card layouts showing total votes count, rating indicators, and quick-add actions.

### 2. 🔍 Smart Personalised Recommendations
* Powered by a **collaborative filtering model** utilizing cosine similarity matrices.
* Search database matching: Type key terms to instantly filter through hundreds of available titles.
* Simply select a book you loved to receive matched recommendation recommendations with similarity scoring indices.

### 3. ⏰ Dynamic Reading Reminders
* Schedule reminders for books from the database or enter completely custom book details.
* Set reading status (*To Read*, *Currently Reading*, *Completed*, *On Hold*) and personalized reading notes.

### 4. 🏷️ Genres & Custom Tagging
* Organize your personal reading shelf using tags like `#Fiction`, `#Self-Help`, `#Sci-Fi`.
* Tag search options allow sorting and filtering shelf cards dynamically.

### 5. 🔔 Multi-Channel Notifications
* **Browser notifications (HTML5 API)**: On page load, triggers a browser notification detailing books due to read today.
* **Desktop notifications (Plyer)**: Fallback OS tray notifications for windows users.
* Reminders only check once per session to maintain a seamless, unobtrusive UX.

---

## 🛠️ Tech Stack & Architecture

* **Frontend Framework**: Streamlit (Python)
* **Custom Styling**: Vanilla CSS (CSS3 variables, CSS keyframe animations, backdrop-filters, custom grids)
* **Data Processing**: Pandas, NumPy
* **Recommendation Engine**: Cosine Similarity matrix calculations over user-item rating pivot matrices.
* **Persistence**: Local JSON storage (`reading_list.json`).

---

## 🚀 Quick Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/book-recommender-system.git
cd book-recommender-system
```

### 2. Create and activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up pre-trained models
Make sure the following pickle (`.pkl`) model files exist in the root folder of the project:
* `books.pkl` — The core dataset containing ISBN mappings, titles, authors, and cover image paths.
* `popular.pkl` — A calculated slice of top-rated popular books.
* `pt.pkl` — The user-item rating pivot matrix used for collaborative filtering.
* `similarity_scores.pkl` — The computed cosine similarity scores matrix.

*(Note: Large raw dataset CSV files like `Books.csv`, `Ratings.csv`, `Users.csv` are ignored via `.gitignore` to keep repository weights light).*

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
├── .gitignore               # Ignored raw datasets, virtual environments, local user DBs
├── app.py                   # Main Streamlit web application & glassmorphic styling sheet
├── requirements.txt         # Required python packages
├── README.md                # Project documentation
├── books.pkl                # Pre-processed books metadata list (ISBN, Title, Image paths)
├── popular.pkl              # Calculated trending books data
├── pt.pkl                   # Pivot table mapping user ratings to books
└── similarity_scores.pkl    # Pre-calculated item-to-item similarity scores matrix
```

---

*Enjoy tracking your next reading quest! 📖✨*
