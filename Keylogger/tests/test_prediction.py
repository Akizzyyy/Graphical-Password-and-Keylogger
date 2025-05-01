from shoulder_surfer_gui import predict_password, PasswordLearner
import torch

def test_predict_emoji_format():
    model = PasswordLearner(output_dim=25)
    model.eval()
    result = predict_password(model, "grid")
    assert isinstance(result, str)  # One emoji

def test_predict_wheel_format():
    model = PasswordLearner(output_dim=18)
    model.eval()
    result = predict_password(model, "wheel")
    assert isinstance(result, list)
    assert len(result) == 3
