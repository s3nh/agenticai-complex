#!/bin/bash
# Install vLLM
pip install vllm

# Option A: Vision model (for scanned docs / images)
vllm serve Qwen/Qwen2.5-VL-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 8192

# Option B: Text-only, lighter weight
# vllm serve mistralai/Mistral-7B-Instruct-v0.3 \
#     --host 0.0.0.0 --port 8000

# Option C: Multi-GPU with tensor parallelism
# vllm serve Qwen/Qwen2.5-VL-72B-Instruct \
#     --tensor-parallel-size 4 --host 0.0.0.0 --port 8000
