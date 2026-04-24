import os

files_to_update = [
    r"tests\test_quality_filter.py",
    r"tests\integration\test_reputation_pipeline.py",
    r"scripts\test_reputation_integration.py",
    r"app\layer2\pipeline_orchestrator.py",
    r"app\api\v1\endpoints\reputation.py"
]

base_dir = r"c:\Users\user\Desktop\National_Indicator\NationalActivityIndicator_MAIN\backend"

for f in files_to_update:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Replace occurrences
        new_content = content.replace("app.services.quality_filter", "app.services.filters")
        
        if new_content != content:
            with open(path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Updated: {f}")
        else:
            print(f"No changes needed: {f}")
    else:
        print(f"File not found: {f}")

print("Done replacing imports.")
