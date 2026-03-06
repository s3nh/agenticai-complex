# 1. Copy and configure env
cp .env.example .env
# edit .env with your GOOGLE_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run with Gemini (cloud)
INFERENCE_MODE=gemini python main.py path/to/invoice.pdf

# 4. Run with local vLLM
# (start vLLM server first - see start_vllm.sh)
INFERENCE_MODE=vllm python main.py path/to/contract_scan.jpg

# 5. Launch ADK Web UI for interactive testing
adk web --port 8080
# Open http://localhost:8080
