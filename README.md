# How to Run

```
pip install -r requirements.txt
```

```
#download https://drive.google.com/file/d/1p7tqNSIfY-GU_GyuJafNvne19fj4AF6Y/view?usp=drive_link
mv chroma_db_chunk_v3.zip app/adapters/outbound/chroma/
unzip chroma_db_chunk_v3.zip
```

```
#make .env file
mv .env app/
```

```
cd app
python -m uvicorn main:app --reload
```


# How to Use (local)

```
python example/start_session.py
```

```
python example/request_to_chatbot.py --session_id="..." --content="..."
```

