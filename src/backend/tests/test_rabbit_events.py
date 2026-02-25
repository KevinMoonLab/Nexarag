from rabbit.events import ChatMessage, DocumentsCreated, EmbeddingPlotCreated


class FakeArray:
    def __init__(self, values):
        self.values = values

    def tolist(self):
        return self.values


def test_chat_message_populates_defaults():
    message = ChatMessage(message="hello", prefix="context")

    assert message.chatId
    assert message.messageId
    assert message.numCtx == 32768
    assert message.numPredict == 4096
    assert message.model == "gemma3:1b"


def test_embedding_plot_created_from_numpy_flattens_ids():
    embeddings_np = FakeArray([[0.1, 0.2], [0.3, 0.4]])
    paper_id_chunks = [FakeArray(["p1", "p2"]), FakeArray(["p3"])]

    created = EmbeddingPlotCreated.from_numpy(embeddings_np, ["a", "b"], paper_id_chunks)

    assert created.embeddings == [[0.1, 0.2], [0.3, 0.4]]
    assert created.labels == ["a", "b"]
    assert created.paper_ids == ["p1", "p2", "p3"]


def test_documents_created_project_id_defaults_to_none():
    event = DocumentsCreated(documents=[])
    assert event.project_id is None
