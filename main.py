from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd
import io

from models import SessionLocal, Feedback

app = FastAPI(title="Dynamic Analytics Engine API")

# Enable Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the static folder so CSS/JS and the HTML file can be accessed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Explicitly serve dashboard.html when users visit your main web link
@app.get("/")
async def serve_frontend():
    return FileResponse("static/dashboard.html")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload-feedback/")
async def upload_feedback(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only standard Excel formatting sheets are allowed")

    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents), sheet_name=0)

    column_sets = [
        {"trainer": "Trainer's Name", "date": "Timestamp", "rating": "Rate your understanding of today’s content  ", "diff": "What difficulties did you face today?  ", "rem": "Any Remarks or suggestions?", "subject": "Select your choice"},
        {"trainer": "Trainer's Name 2", "date": "Timestamp", "rating": "Rate your understanding of today’s content   2", "diff": "What difficulties did you face today?   2", "rem": "Any Remarks or suggestions? 2", "subject": "Select your choice"},
        {"trainer": "Trainer's Name 3", "date": "Timestamp", "rating": "Rate your understanding of today’s content   3", "diff": "What difficulties did you face today?   3", "rem": "Any Remarks or suggestions? 3", "subject": "Select your choice"},
        {"trainer": "Trainer's Name 4", "date": "Timestamp", "rating": "Rate your understanding of today’s content   4", "diff": "What difficulties did you face today?   4", "rem": "Any Remarks or suggestions? 4", "subject": "Select your choice"}
    ]

    records_added = 0

    for index, row in df.iterrows():
        for col_set in column_sets:
            if col_set["trainer"] in row and pd.notna(row[col_set["trainer"]]):
                raw_date = row.get(col_set["date"])
                parsed_date = datetime.now().date()
                if pd.notna(raw_date):
                    parsed_date = pd.to_datetime(raw_date).date()

                subject_val = str(row.get(col_set["subject"], "General"))
                if subject_val.lower() == "nan" or subject_val.strip() == "":
                    subject_val = "General"

                feedback = Feedback(
                    trainer_name=str(row[col_set["trainer"]]),
                    date=parsed_date,
                    subject=subject_val.strip(),
                    rating=float(row.get(col_set["rating"], 0)),
                    difficulties=str(row.get(col_set["diff"], "")),
                    remarks=str(row.get(col_set["rem"], ""))
                )
                db.add(feedback)
                records_added += 1

    db.commit()
    return {"message": f"Successfully processed and cataloged {records_added} feedback logs into the database!"}

@app.get("/api/dashboard-data/")
def get_dashboard_data(db: Session = Depends(get_db)):
    records = db.query(Feedback).all()
    return [
        {
            "Trainer": r.trainer_name,
            "Date": r.date.strftime("%Y-%m-%d"),
            "Rating": r.rating,
            "Subject": r.subject,
            "Difficulties": r.difficulties,
            "Remarks": r.remarks
        } for r in records
    ]
