from ai_generator import get_keywords_from_ai

print("Testing AI keyword generation...")
try:
    keywords = get_keywords_from_ai("浴室柜", 5)
    print(f"Generated keywords: {keywords}")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
