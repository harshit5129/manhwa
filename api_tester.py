import requests
import time
import sys
import json

BASE_URL = "http://localhost:5000"

def log(msg):
    print(f"[TEST] {msg}")

def wait_for_server():
    log("Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                log("Server is up!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    log("Server failed to start or is not reachable.")
    return False

def test_create_project():
    log("Testing Create Project...")
    payload = {"title": "Test Project"}
    try:
        response = requests.post(f"{BASE_URL}/api/projects", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                project_id = data["project"]["project_id"]
                log(f"Project created: {project_id}")
                return project_id
            else:
                log(f"Failed to create project: {data.get('error')}")
        else:
            log(f"Failed to create project. Status: {response.status_code}")
    except Exception as e:
        log(f"Exception creating project: {e}")
    return None

def test_create_character():
    log("Testing Create Character...")
    payload = {
        "name": "Test Char",
        "gender": "female",
        "age": "20",
        "hair_color": "blue",
        "eye_color": "green",
        "default_outfit": "casual"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/characters", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                char_id = data["character"]["character_id"]
                log(f"Character created: {char_id}")
                return char_id
            else:
                log(f"Failed to create character: {data.get('error')}")
        else:
            log(f"Failed to create character. Status: {response.status_code}")
    except Exception as e:
        log(f"Exception creating character: {e}")
    return None

def test_generation(project_id):
    log("Testing Generation Start...")
    payload = {
        "chapter_text": "Elena stood at the cliff edge. The wind blew through her hair.",
        "model": "sd15",
        "style": "manhwa",
        "quality": "draft",
        "max_panels": 1
    }
    try:
        response = requests.post(f"{BASE_URL}/api/generate", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                job_id = data["job_id"]
                log(f"Generation started. Job ID: {job_id}")
                return job_id
            else:
                log(f"Failed to start generation: {data.get('error')}")
        else:
            log(f"Failed to start generation. Status: {response.status_code}")
            log(f"Response: {response.text}")
    except Exception as e:
        log(f"Exception starting generation: {e}")
    return None

def check_progress(job_id):
    log(f"Checking progress for job {job_id}...")
    for i in range(30): # Wait up to 60 seconds
        try:
            response = requests.get(f"{BASE_URL}/api/progress/{job_id}")
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                progress = data.get("progress")
                log(f"Status: {status}, Progress: {progress}%")
                
                if status == "completed":
                    log("Generation completed successfully!")
                    return True
                elif status == "failed":
                    log(f"Generation failed: {data.get('error')}")
                    return False
            else:
                log(f"Failed to get progress. Status: {response.status_code}")
        except Exception as e:
            log(f"Exception checking progress: {e}")
        time.sleep(2)
    log("Timed out waiting for generation.")
    return False

def main():
    if not wait_for_server():
        sys.exit(1)
    
    project_id = test_create_project()
    if not project_id:
        sys.exit(1)
        
    char_id = test_create_character()
    
    job_id = test_generation(project_id)
    if job_id:
        check_progress(job_id)

if __name__ == "__main__":
    main()
