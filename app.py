# import requests
# from bs4 import BeautifulSoup
# import csv
# import io
# import time
# import logging
# from fastapi import FASTAPI,form,Request,HTTPException
# from fastapi.responses import HTMLResponse,StreamingResponse,TemplateResponse
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel

# app = FastAPI()
# templates = Jinja2Templates(directory="templates")


# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Function to scrape GitHub repositories
# def scrape_github_repos(topic, num_repos):
#     url = f"https://github.com/topics/{topic}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Request failed: {e}")
#         return None

#     soup = BeautifulSoup(response.text, 'html.parser')

#     repos = []
#     repo_elements = soup.find_all('article', class_='border rounded color-shadow-small color-bg-subtle my-4', limit=num_repos)

#     for repo in repo_elements:
#         repo_name = repo.find('h3').text.strip() if repo.find('h3') else "No Name"
#         repo_url = "https://github.com" + repo.find('a')['href'] if repo.find('a') else "No URL"
        
#         # Handle cases where the stars element might be missing
#         stars_element = repo.find('span', class_='Counter js-social-count')
#         stars = stars_element.text.strip() if stars_element else "0"

#         repos.append([repo_name, repo_url, stars])

#     return repos

# # @app.route('/', methods=['GET', 'POST'])
# # def index():
# #     if request.method == 'POST':
# #         topic = request.form['topic']
# #         num_repos = int(request.form['num_repos'])
# #         repos = scrape_github_repos(topic, num_repos)

# #         if repos is None:
# #             flash("Failed to fetch repositories. Please try again later.", "error")
# #             return redirect(url_for('index'))

# #         return render_template('index.html', repos=repos, topic=topic)

# #     return render_template('index.html', repos=None)

# @app.get('/', response_class=HTMLResponse)
# async def index(request: Request):
#     """Render homepage (GET only)."""
#     return templates.TemplateResponse("index.html", {"request": request, "repos": None})

# @app.post('/', response_class=HTMLResponse)
# async def fetch_repos(request: Request, topic: str = Form(...), num_repos: int = Form(...)):
#     """Handle form submission (POST)."""
#     repos = scrape_github_repos(topic, num_repos)

#     if repos is None:
#         raise HTTPException(status_code=500, detail="Failed to fetch repositories")

#     return templates.TemplateResponse(
#         "index.html",
#         {"request": request, "repos": repos, "topic": topic}
#     )

# @app.get("/download_csv/{topic}/{num_repos}")
# async def download_csv(topic: str, num_repos: int):
#     """Download GitHub repos as CSV."""
#     repos = scrape_github_repos(topic, num_repos)

#     if repos is None:
#         raise HTTPException(status_code=500, detail="Failed to fetch repositories")

#     # Create CSV in-memory
#     output = io.StringIO()
#     writer = csv.writer(output)
#     writer.writerow(['Repository Name', 'Repository URL', 'Stars'])
#     writer.writerows(repos)
#     output.seek(0)

#     # Send CSV file
#     return StreamingResponse(
#         io.StringIO(output.getvalue()),
#         media_type="text/csv",
#         headers={"Content-Disposition": f"attachment; filename={topic}_top_{num_repos}_repos.csv"}
#     )


# # @app.route('/download_csv/<topic>/<int:num_repos>', methods=['GET'])
# # def download_csv(topic, num_repos):
# #     repos = scrape_github_repos(topic, num_repos)

# #     if repos is None:
# #         flash("Failed to fetch repositories. Please try again later.", "error")
# #         return redirect(url_for('index'))

# #     # Generate CSV
# #     output = io.StringIO()
# #     writer = csv.writer(output)
# #     writer.writerow(['Repository Name', 'Repository URL', 'Stars'])
# #     writer.writerows(repos)

# #     output.seek(0)
    
# #     return send_file(io.BytesIO(output.getvalue().encode('utf-8')), 
# #                      mimetype='text/csv', 
# #                      as_attachment=True, 
# #                      download_name=f"{topic}_top_{num_repos}_repos.csv")

# if __name__ == '__main__':
#     app.run(debug=True)
import requests
from bs4 import BeautifulSoup
import csv
import io
import logging
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to scrape GitHub repositories
def scrape_github_repos(topic: str, num_repos: int):
    url = f"https://github.com/topics/{topic}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    repos = []
    repo_elements = soup.find_all(
        'article',
        class_='border rounded color-shadow-small color-bg-subtle my-4',
        limit=num_repos
    )

    for repo in repo_elements:
        repo_name = repo.find('h3').text.strip() if repo.find('h3') else "No Name"
        repo_url = "https://github.com" + repo.find('a')['href'] if repo.find('a') else "No URL"
        stars_element = repo.find('span', class_='Counter js-social-count')
        stars = stars_element.text.strip() if stars_element else "0"

        repos.append([repo_name, repo_url, stars])

    return repos


# Home page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "repos": None})


# Form submission
@app.post("/", response_class=HTMLResponse)
async def fetch_repos(request: Request, topic: str = Form(...), num_repos: int = Form(...)):
    repos = scrape_github_repos(topic, num_repos)

    if repos is None:
        raise HTTPException(status_code=500, detail="Failed to fetch repositories")

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "repos": repos, "topic": topic}
    )


# Download CSV
@app.get("/download_csv/{topic}/{num_repos}")
async def download_csv(topic: str, num_repos: int):
    repos = scrape_github_repos(topic, num_repos)

    if repos is None:
        raise HTTPException(status_code=500, detail="Failed to fetch repositories")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Repository Name', 'Repository URL', 'Stars'])
    writer.writerows(repos)
    output.seek(0)

    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={topic}_top_{num_repos}_repos.csv"
        }
    )

