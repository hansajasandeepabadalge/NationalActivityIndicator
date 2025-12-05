try:
    import sqlalchemy
    print(f"sqlalchemy: {sqlalchemy.__version__}")
    import pymongo
    print(f"pymongo: {pymongo.__version__}")
    import redis
    print(f"redis: {redis.__version__}")
    print("Imports successful")
except Exception as e:
    print(f"Import failed: {e}")
except ImportError as e:
    print(f"ImportError: {e}")
