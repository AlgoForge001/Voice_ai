from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoConfig

model_id = "ai4bharat/indic-parler-tts"

print("Loading config...")
config = AutoConfig.from_pretrained(model_id)
print("Config loaded:", config)

print("Loading model...")
# Try loading without safetensors first if applicable, or specify device map
model = ParlerTTSForConditionalGeneration.from_pretrained(model_id)
print("Model loaded!")
