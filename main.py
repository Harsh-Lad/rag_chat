import os
from mongo_manager import MongoDBClient
from s3_manager import S3Client
from text_utils import TextUtils
from embedding_utils import EmbeddingUtils  
from datetime import datetime
from io import BytesIO
from chat_utils import ChatUtils

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
bucket_name = os.environ.get('S3_BUCKET_NAME')
mongo_uri = os.environ.get('MONGO_URI')
mongo_db_name = os.environ.get('MONGO_DB_NAME')

def main():
    file_url = 'https://intern-assignment-demo.s3.ap-south-1.amazonaws.com/tesla.pdf' 
    s3_client = S3Client(aws_access_key_id, aws_secret_access_key, bucket_name)
    file_obj = s3_client.download_file(file_url)

    if file_obj:
        text_utils = TextUtils()

        try:
            file_extension = os.path.splitext(file_url)[1]
            extracted_text = text_utils.extract_text(file_obj, file_extension)
            chunks = text_utils.chunk_text(extracted_text)
            print(f"Number of chunks: {len(chunks)}\n")

            embedding_utils = EmbeddingUtils()

            embeddings = embedding_utils.generate_embeddings(chunks)
            print(f"Number of embeddings: {len(embeddings)}\n")

            pickled_chunks = text_utils.pickle_data(chunks)
            pickled_embeddings = text_utils.pickle_data(embeddings)
            print(f"Pickled chunks size: {len(pickled_chunks)} bytes\n")
            print(f"Pickled embeddings size: {len(pickled_embeddings)} bytes\n")

            pickled_chunks_io = BytesIO(pickled_chunks)
            pickled_embeddings_io = BytesIO(pickled_embeddings)

            file_key = file_url.split('/')[-1]
            current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
            embeddings_key = f"chatbot/embeddings/{file_key}_{current_datetime}_embeddings.pkl"
            chunks_key = f"chatbot/chunks/{file_key}_{current_datetime}_chunks.pkl"

            embeddings_url = s3_client.upload_file(pickled_embeddings_io, embeddings_key)
            chunks_url = s3_client.upload_file(pickled_chunks_io, chunks_key)

            if embeddings_url and chunks_url:
                print(f"Embeddings uploaded to: {embeddings_url}")
                print(f"Chunks uploaded to: {chunks_url}")

                mongo_client = MongoDBClient(mongo_uri, mongo_db_name)
                mongo_client.insert_document('contexts', {'file_name': file_key, 'embeddings_key': embeddings_key, 'chunks_key': chunks_key, 'datetime': current_datetime})
                mongo_client.close_connection()
            else:
                print("Error uploading embeddings and chunks to S3")

        except ValueError as e:
            print(f"Error: {e}")

def chatbot():
    file_name = 'tesla.pdf' 
    mongo_client = MongoDBClient(mongo_uri, mongo_db_name)
    document = mongo_client.db['contexts'].find_one({'file_name': file_name})
    mongo_client.close_connection()

    if document:
        embeddings_key = document['embeddings_key']
        chunks_key = document['chunks_key']

        s3_client = S3Client(aws_access_key_id, aws_secret_access_key, bucket_name)
        embeddings_file_obj = s3_client.download_file(embeddings_key)
        chunks_file_obj = s3_client.download_file(chunks_key)

        if embeddings_file_obj and chunks_file_obj:
            text_utils = TextUtils()
            embeddings = text_utils.unpickle_data(embeddings_file_obj.read())
            chunks = text_utils.unpickle_data(chunks_file_obj.read())
            print(f"Number of embeddings: {len(embeddings)}")
            print(f"Number of chunks: {len(chunks)}")
        else:
            print("Error downloading embeddings and chunks from S3")
    
    else:
        print("Document not found in MongoDB")

    user_input = "Does tesla has abs ? If yes then send an email to harshplad@gmail.com with the details"

    embedding_utils = EmbeddingUtils()
    user_input_embedding = embedding_utils.generate_embeddings([user_input])

    similar_chunks = embedding_utils.find_similar_chunks(user_input_embedding, embeddings, chunks, k=5)

    chat_utils = ChatUtils()

    context = similar_chunks
    response = chat_utils.generate_response(f'Query: {user_input}, Context :{context}')
    print(f"Response: {response}")


if __name__ == '__main__':
    # main()
    chatbot()