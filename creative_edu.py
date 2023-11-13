from langchain.document_loaders import UnstructuredURLLoader

loader = UnstructuredURLLoader(
    urls=["https://creative.edu.hk"], mode="elements", strategy="fast",
)
docs = loader.load()

print(docs)
