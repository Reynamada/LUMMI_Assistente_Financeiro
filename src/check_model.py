import requests, os, json

key = os.getenv("OPENROUTER_API_KEY")
# Test 1: Check if the current model works
print("=== Testando modelo atual ===")
r = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "openai/gpt-oss-120b:free",
        "messages": [{"role": "user", "content": "Diga apenas: OK"}]
    },
    timeout=30
)
data = r.json()
if "choices" in data:
    print("MODELO OK:", data["choices"][0]["message"]["content"])
else:
    print("ERRO:", json.dumps(data, indent=2, ensure_ascii=False))

# Test 2: List free models
print("\n=== Modelos gratuitos disponíveis ===")
r2 = requests.get("https://openrouter.ai/api/v1/models")
free_models = [m["id"] for m in r2.json().get("data", []) if ":free" in m["id"]]
for m in sorted(free_models):
    print(f"  {m}")
