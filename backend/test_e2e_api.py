!!!import requests
import time
import sys
import uuid

BASE_URL = "https://edudeck-backend.onrender.com/api/v1"

def print_step(msg):
    print(f"\n[STEP] {msg}")

def main():
    session = requests.Session()
    
    # 1. Register / Login
    print_step("Registering a test user")
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"
    
    res = session.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "E2E Tester"
    })
    if res.status_code != 200:
        print("Registration failed:", res.text)
        sys.exit(1)
        
    print_step("Logging in")
    res = session.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    if res.status_code != 200:
        print("Login failed:", res.text)
        sys.exit(1)
        
    token = res.json()["data"]["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("Token acquired!")

    # 2. Create Project
    print_step("Creating a project")
    res = session.post(f"{BASE_URL}/projects/", json={
        "title": "E2E Test Project",
        "description": "Testing the MVP flow"
    })
    if res.status_code not in (200, 201):
        print("Project creation failed:", res.text)
        sys.exit(1)
        
    project_id = res.json()["data"]["id"]
    print(f"Project ID: {project_id}")

    # 3. Upload PDF
    print_step("Uploading document")
    # We'll use the Alice in Wonderland PDF we downloaded
    pdf_path = "alice.pdf"
    
    with open(pdf_path, "rb") as f:
        files = {"file": ("alice.pdf", f, "application/pdf")}
        data = {'project_id': project_id}
        res = session.post(f"{BASE_URL}/documents/upload", files=files, data=data)
        
    if res.status_code != 200:
        print("Upload failed:", res.text)
        sys.exit(1)
        
    doc_id = res.json()["data"]["id"]
    print(f"Document ID: {doc_id}")

    # 4. Wait for processing
    print_step("Polling for document processing progress...")
    while True:
        res = session.get(f"{BASE_URL}/documents/{doc_id}/progress")
        if res.status_code != 200:
            print("Failed to get progress:", res.text)
            sys.exit(1)
            
        status = res.json()["data"]["status"]
        print(f"Status: {status}")
        if status == "ready":
            print("Document processing complete!")
            break
        elif status == "failed":
            print("Document processing failed!")
            sys.exit(1)
        time.sleep(2)

    # 5. Generate PPTX
    print_step("Requesting AI Generation (this may take 10-30 seconds)")
    res = session.post(f"{BASE_URL}/generation/generate", json={
        "project_id": project_id,
        "prompt": "Create a 5 slide presentation summarizing Chapter 1: Down the Rabbit Hole. Include key events, the white rabbit, and Alice falling down the hole."
    })
    
    if res.status_code != 200:
        print("Generation failed:", res.text)
        sys.exit(1)
        
    download_url = res.json()["data"]["download_url"]
    print("\nSUCCESS! Presentation generated.")
    print("Download URL:", download_url)

if __name__ == "__main__":
    main()
