import torch
from shoulder_surfer_gui import PasswordLearner

def test_forward_pass_wheel():
    model = PasswordLearner(output_dim=18)
    dummy_input = torch.randn(1, 3, 256, 256)
    output = model(dummy_input)
    assert output.shape == (1, 18)

def test_forward_pass_emoji():
    model = PasswordLearner(output_dim=25)
    dummy_input = torch.randn(1, 3, 256, 256)
    output = model(dummy_input)
    assert output.shape == (1, 25)
