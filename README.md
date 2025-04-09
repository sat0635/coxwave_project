# How to Set Up

```
#dev (fastapi, example scripts, data preprocessing scripts)
poetry install --with=dev

#real (fastapi)
poetry install --without=dev
```

# How to Run Server

```
#download https://drive.google.com/file/d/1NnbdTXBZnvw8evbYWARmW_rIZI1CqVl4/view?usp=sharing
mv chroma_db_chunk_v3.zip app/adapters/outbound/chroma/
unzip chroma_db_chunk_v3.zip
```

```
#make .env file
mv .env app/
```

```
poetry run python -m uvicorn app.main:app --reload
```

# How to Make ChromaDB data

```
cd scripts

# original Q&A pkl to refined jsonl
poetry run python make_refined_faq_answer_question.py
# add topic keywords on each jsonl Q&A
poetry run python bertopic_soft_clustering_v4.py

cd ..

mv scripts/faq_answer_question_pair_with_categories_v4.jsonl app/adapters/outbound/chroma

# run server
# in 1-2 hours
# app/adapters/outbound/chroma/chroma_db_chunk_v3 will be created
# and fastapi will be lunched
```

# How to Use (local)

```
poetry run python example/start_session.py
```

```
poetry run python example/request_to_chatbot.py --session_id="..." --content="..."
```

# System Components
![image](https://github.com/user-attachments/assets/7dd81cf4-0eca-454f-b0e1-d470c0a4064b)
