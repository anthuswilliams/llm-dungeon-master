

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.vectorstores import LanceDB
from langchain.embeddings.openai import OpenAIEmbeddings
import lancedb
import pyarrow as pa

from langchain.document_loaders import TextLoader

def load_character_sheet(path):
    loader = TextLoader(path)
    return loader.load()


def connect():
    embedding_function = OpenAIEmbeddings()

    db = lancedb.connect('db')
    table = db.open_table('characters')
    return LanceDB(table, embedding_function)


def generate_character_embeddings(path):
    embeddings = OpenAIEmbeddings()
    
    db = lancedb.connect("db")
    character_sheet = load_character_sheet(path)
    table = db.create_table(
        "characters",
         data=[
            {
                "vector": embeddings.embed_query("Hello World"),
                "text": "Hello World",
                "id": "1",
            }
        ],
        mode="overwrite",
    )

    # Load the document, split it into chunks, embed each chunk and load it into the vector store.
    db = LanceDB.from_documents(character_sheet, embeddings, connection=table)
    query = "What is Nebula's equipment?"
    docs = db.similarity_search(query)
    print(docs)


def retriever():
    # Create a retriever that fetches documents from multiple tables
    lance_retriever = connect().as_retriever()

    template = """Answer the question based only on the following context:
    {context}.

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI()

    return (
        {"context": lance_retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    
# Create a retriever that fetches documents from multiple tables
if __name__ == "__main__":
    # generate_character_embeddings("agents/05_formatted.json")
    print(retriever().invoke("What is Nebula's equipment?"))