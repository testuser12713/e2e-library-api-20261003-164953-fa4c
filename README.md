# Bibliotheksausleihe API

Eine FastAPI-REST-API für die Ausleihe einer kleinen Stadtbibliothek: Verwaltung
von Büchern und Mitgliedern (CRUD), Ausleihen mit Rückgabe, Überfälligenliste und
Buchsuche mit Paginierung. Persistenz über SQLAlchemy 2.0 in SQLite, Validierung
mit Pydantic v2, Schutz aller schreibenden Endpunkte per API-Key.

## Tech Stack

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- SQLite
- uvicorn
- pytest + FastAPI TestClient

## Installation

```bash
python -m pip install -r requirements.txt
```

## Start (Entwicklung)

Die API startet nur, wenn `API_KEY` in der Umgebung gesetzt ist — es gibt keinen
Default-Wert. Einen eigenen Key wählen und exportieren (kopierbarer Startbefehl):

```bash
export API_KEY="dein-geheimer-api-key"          # macOS / Linux
python -m uvicorn app.main:app --port 8000
```

```powershell
$env:API_KEY = "dein-geheimer-api-key"          # Windows (PowerShell)
python -m uvicorn app.main:app --port 8000
```

Danach ist die API unter `http://localhost:8000` erreichbar, die interaktive
API-Dokumentation unter `http://localhost:8000/docs`.

## Umgebungsvariablen

| Variable       | Pflicht | Default                  | Beschreibung                                   |
| -------------- | ------- | ------------------------ | ---------------------------------------------- |
| `DATABASE_URL` | nein    | `sqlite:///./library.db` | Verbindungs-URL der Datenbank                  |
| `API_KEY`      | ja      | –                        | API-Key für alle schreibenden Endpunkte        |

`API_KEY` hat bewusst keinen Default: Der Start über die Ausführungsumgebung
(`RUN.json`) erzeugt den Key pro Lauf automatisch (`generate`). Lokal setzt man
ihn wie oben beschrieben selbst — es ist derselbe Wert, der anschließend im
Header `X-API-Key` mitgeschickt werden muss.

Die Datenbank (SQLite-Datei) und ihre Tabellen werden beim Start automatisch
angelegt — es ist keine manuelle Migration nötig.

## API-Key

Alle schreibenden Endpunkte (`POST`, `PUT`, `DELETE`) verlangen den Header
`X-API-Key` mit dem Wert aus `API_KEY`. Ohne bzw. mit falschem Key antwortet die
API mit `401`.

## Endpunkte

Jede Fehlerantwort hat die Form `{"detail": "..."}`.

| Methode | Pfad                       | Auth | Erfolg | Beschreibung                          |
| ------- | -------------------------- | ---- | ------ | ------------------------------------- |
| GET     | `/health`                  | –    | 200    | Health-Check `{"status":"ok"}`        |
| GET     | `/books`                   | –    | 200    | Buchsuche mit Paginierung             |
| GET     | `/books/{book_id}`         | –    | 200    | Einzelnes Buch                        |
| POST    | `/books`                   | Key  | 201    | Buch anlegen                          |
| PUT     | `/books/{book_id}`         | Key  | 200    | Buch aktualisieren                    |
| DELETE  | `/books/{book_id}`         | Key  | 204    | Buch löschen                          |
| GET     | `/members`                 | –    | 200    | Alle Mitglieder                       |
| GET     | `/members/{member_id}`     | –    | 200    | Einzelnes Mitglied                    |
| POST    | `/members`                 | Key  | 201    | Mitglied anlegen                      |
| PUT     | `/members/{member_id}`     | Key  | 200    | Mitglied aktualisieren                |
| DELETE  | `/members/{member_id}`     | Key  | 204    | Mitglied löschen                      |
| POST    | `/loans`                   | Key  | 201    | Ausleihe anlegen                      |
| POST    | `/loans/{loan_id}/return`  | Key  | 200    | Ausleihe zurückgeben                  |
| GET     | `/loans/overdue`           | –    | 200    | Überfällige Ausleihen auflisten       |

### Buchsuche (GET /books)

- Query-Parameter: `q` (Suche nach Titel/Autor, case-insensitiv), `limit`
  (Default 20, max. 100), `offset` (Default 0).
- Antwort: `{"items": [BookOut], "total": int, "limit": int, "offset": int}`.

## Tests

```bash
python -m pytest
```

Die Test-Suite läuft gegen eine isolierte In-Memory-SQLite-Datenbank und
verändert niemals die Entwicklungsdatenbank.
