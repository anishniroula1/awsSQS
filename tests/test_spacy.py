import pytest
from unittest.mock import patch

from spacy import SpacySingleton

def test_get_model_returns_model():
    model = SpacySingleton.get_model()
    assert model is not None

def test_get_model_singleton():
    model1 = SpacySingleton.get_model()
    model2 = SpacySingleton.get_model()
    assert model1 is model2

@patch('spacy.load', side_effect=Exception("Mocked exception"))
def test_get_model_exception(mocked_spacy_load):
    with pytest.raises(Exception) as exc_info:
        SpacySingleton.get_model()
    assert "Mocked exception" in str(exc_info.value)

def test_get_vocab_returns_vocab():
    vocab = SpacySingleton.get_vocab()
    assert isinstance(vocab, frozenset)

def test_get_vocab_singleton():
    vocab1 = SpacySingleton.get_vocab()
    vocab2 = SpacySingleton.get_vocab()
    assert vocab1 is vocab2

def test_get_vocab_uses_model_vocab():
    model = SpacySingleton.get_model()
    vocab = SpacySingleton.get_vocab()
    assert all(word in vocab for word in model.vocab.strings)
