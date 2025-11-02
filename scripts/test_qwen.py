"""Test Qwen API key"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_qwen():
    from openai import AsyncOpenAI
    
    api_key = os.getenv("QWEN_API_KEY", "")
    
    print("=" * 60)
    print("QWEN API KEY TEST")
    print("=" * 60)
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    print(f"API Key length: {len(api_key)} chars")
    print("=" * 60)
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
        
        print("\nTesting Qwen API call...")
        
        response = await client.chat.completions.create(
            model="qwen-max",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello! Qwen is working!' in one sentence."}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        
        print("\nSUCCESS! Qwen API is working!")
        print(f"\nQwen's response: {result}")
        print("\n" + "=" * 60)
        print("Your Qwen API key is valid and working!")
        print("You can now use it for trading.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING:")
        print("=" * 60)
        print("1. Check your API key is correct")
        print("2. Verify it's from: https://dashscope.console.aliyun.com/")
        print("3. Make sure it has API access (not just billing)")
        print("4. Try regenerating a new API key")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_qwen())

