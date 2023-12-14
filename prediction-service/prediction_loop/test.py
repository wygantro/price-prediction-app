import pickle
from google.cloud import storage

# Google Cloud Storage information
bucket_name = 'mlflow-models-nycdsa-project-4'
file_name = '0/6ddcd5b6d4f8473dafc6b93fedbe4b94/artifacts/model_1702409601/model.pkl'

# initialize a client to interact with Google Cloud Storage
storage_client = storage.Client()

# get the model bucket and pickle file
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(file_name)

try:
    # download the pickle file from Google Cloud Storage
    binary_model = blob.download_as_bytes()

    # deserialize the binary model using pickle
    model = pickle.loads(binary_model)

    # print loaded ML model
    print(model)

except Exception as e:
    print(f"An error occurred: {e}")

