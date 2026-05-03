from google import genai

client = genai.Client(api_key="AIzaSyAipjXBpomG_PwnBNlrD83rzQ2nOBXX0MI")

for model in client.models.list():
    print(model.name)