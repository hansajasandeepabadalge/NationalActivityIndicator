import os

files_to_update = [
    r"tests\test_reputation_system.py",
    r"tests\integration\test_reputation_pipeline.py",
    r"scripts\test_reputation_integration.py",
    r"app\services\__init__.py",
    r"app\services\quality_filter.py",
    r"app\orchestrator\master_orchestrator.py",
    r"app\learning\feedback_loop.py",
    r"app\api\v1\endpoints\reputation.py"
]

base_dir = r"c:\Users\user\Desktop\National_Indicator\NationalActivityIndicator_MAIN\backend"

for f in files_to_update:
    path = os.path.join(base_dir, f)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Replace occurrences
        new_content = content.replace("app.services.reputation_manager", "app.services.reputation")
        
        if new_content != content:
            with open(path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Updated: {f}")
        else:
            print(f"No changes needed: {f}")
    else:
        print(f"File not found: {f}")

print("Done replacing imports.")
