# verify_install.py
import sys

print("=" * 50)
print("RAYHUB AI LMS - DEPENDENCY VERIFICATION")
print("=" * 50)
print(f"Python Path: {sys.executable}")
print(f"Python Version: {sys.version}")
print("=" * 50)

# List of packages to check
packages = {
    "Web Framework": ["fastapi", "uvicorn"],
    "Database": ["sqlalchemy", "pymysql"],
    "Authentication": ["jose", "passlib", "cryptography", "bcrypt"],
    "Data Validation": ["pydantic", "pydantic_settings", "python_dotenv"],
    "AI & ML": ["openai", "langchain", "sentence_transformers", "numpy", "faiss"],
    "Document Processing": ["PyPDF2", "bs4"],
    "Utilities": ["requests", "youtube_transcript_api", "multipart"]
}

all_passed = True

for category, libs in packages.items():
    print(f"\n[{category}]")
    for lib in libs:
        try:
            # Handle special import names
            if lib == "jose":
                __import__("jose")
            elif lib == "bs4":
                __import__("bs4")
            elif lib == "pydantic_settings":
                __import__("pydantic_settings")
            elif lib == "python_dotenv":
                __import__("dotenv")
            elif lib == "multipart":
                __import__("multipart")
            elif lib == "youtube_transcript_api":
                __import__("youtube_transcript_api")
            else:
                __import__(lib)
            print(f"  ✓ {lib} - OK")
        except ImportError as e:
            print(f"  ✗ {lib} - MISSING: {e}")
            all_passed = False

print("\n" + "=" * 50)
if all_passed:
    print("✅ ALL DEPENDENCIES INSTALLED CORRECTLY!")
    print("=" * 50)
    print("\nYou can now run: uvicorn app.main:app --reload")
else:
    print("❌ SOME DEPENDENCIES ARE MISSING")
    print("=" * 50)
    print("\nRun this command to install missing packages:")
    print("pip install -r requirements.txt")