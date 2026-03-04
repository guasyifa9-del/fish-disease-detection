"""Test script untuk debug model loading."""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

model_path = os.path.join(os.path.dirname(__file__), 'models', 'best_model.h5')

print(f"Model path: {model_path}")
print(f"File exists: {os.path.exists(model_path)}")
print(f"File size: {os.path.getsize(model_path) / 1024 / 1024:.1f} MB")

print("\nLoading TensorFlow...")
try:
    import tensorflow as tf
    print(f"TensorFlow version: {tf.__version__}")
except ImportError as e:
    print(f"ERROR: TensorFlow not installed: {e}")
    exit(1)

print("\nLoading model...")
try:
    model = tf.keras.models.load_model(model_path)
    print(f"SUCCESS!")
    print(f"Input shape: {model.input_shape}")
    print(f"Output shape: {model.output_shape}")
except Exception as e:
    print(f"ERROR loading model: {type(e).__name__}: {e}")
