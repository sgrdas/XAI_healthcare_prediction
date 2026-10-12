"""
Explainable AI Health Framework - Root Entry Point
===================================================
Allows running the application directly from the root workspace folder:
    python app.py
"""

import os
import sys
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "Major_project-main")

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.chdir(PROJECT_DIR)

# Dynamically import create_app from the inner app.py
spec = importlib.util.spec_from_file_location("main_app_module", os.path.join(PROJECT_DIR, "app.py"))
app_module = importlib.util.module_from_spec(spec)
sys.modules["main_app_module"] = app_module
spec.loader.exec_module(app_module)

create_app = app_module.create_app

if __name__ == "__main__":
    env_name = os.environ.get("FLASK_ENV", "development")
    application = create_app(env_name)
    port = int(os.environ.get("PORT", 5000))
    use_reloader = os.environ.get("FLASK_USE_RELOADER", "0").lower() in ("true", "1", "yes")
    print(f"\n========================================================")
    print(f"  * Application running at: http://127.0.0.1:{port}")
    print(f"  * Admin Login: admin@healthai.com | Password: Admin@1234")
    print(f"========================================================\n")
    application.run(
        host="0.0.0.0",
        port=port,
        debug=application.config.get("DEBUG", True),
        use_reloader=use_reloader,
    )
