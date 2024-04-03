import spacy


class SpacySingleton:
    model = None
    vocab = None

    @staticmethod
    def get_model():
        if not SpacySingleton.model:
            try:
                SpacySingleton.model = spacy.load(
                    "en_core_web_md",
                    max_length=2000000,
                    disable=["tagger", "parser", "ner"],
                )
            except Exception:
                print("Run")
        return SpacySingleton.model

    @staticmethod
    def get_vocab():
        if not SpacySingleton.vocab:
            SpacySingleton.vocab = frozenset(
                {word.lower() for word in SpacySingleton.get_model().vocab.strings}
            )
            return SpacySingleton.vocab
