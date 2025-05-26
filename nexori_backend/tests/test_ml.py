# tests/test_ml.py
import json
import pytest
from app.ml import model as ml_model
import numpy as np

def test_preprocess_input():
    input_data = {"question1": 5, "question2": 7, "question3": 8}
    features = ml_model.preprocess_input(input_data)
    # Ожидается массив с тремя элементами
    assert features.shape == (1, 3)
    np.testing.assert_array_equal(features, np.array([[5.0, 7.0, 8.0]]))

def test_prediction():
    # Генерируем предсказание для входных данных
    input_data = {"question1": 10, "question2": 10, "question3": 10}
    result = ml_model.predict(input_data)
    assert "predicted_category" in result
    assert "probabilities" in result
    # Вероятности должны суммироваться примерно до 100%
    total = sum(result["probabilities"].values())
    assert abs(total - 100) < 1e-3
