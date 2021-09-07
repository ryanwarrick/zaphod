import json
import os

import requests
from flask import Blueprint, current_app, render_template, send_file
from zaphod.models import md_to_html

bp = Blueprint("career",
               __name__,
               url_prefix="/career",
               template_folder='templates',
               static_folder="static"
               )


def get_project_repos():
    project_repos_file_path = os.path.join(
        current_app.instance_path,
        'content',
        'project_repos.json'
    )
    with open(project_repos_file_path, 'r') as f:
        data = json.load(f)
    return data


@bp.route('/resume')
def resume():
    resume_file_name = current_app.config['RESUME_FILE_NAME']
    resume_file_path = os.path.join(
        current_app.instance_path,
        'content',
        'misc_assets',
        resume_file_name
    )
    return send_file(resume_file_path, download_name=resume_file_name)


@bp.route('/projects')
def projects():
    project_repos = get_project_repos()
    return render_template('career/projects.html', projects=project_repos)


@bp.route('/projects/<project>')
def project(project):
    project_repos = get_project_repos()
    readme_url = "https://raw.githubusercontent.com/ryanwarrick/{project}/master/README.md".format(
        project=project)
    readme_request = requests.get(readme_url)
    readme_md_text = readme_request.text
    readme_md_text = readme_md_text.replace(
        '(docs/images/', "(" + project_repos[project]['raw_content_repo_url'] + 'docs/images/')
    payload = {
        "accept": "application/vnd.github.v3+json",
        "text": readme_md_text,
        "mode": "markdown"
    }
    github_markdown_conversion_request = requests.post(
        'https://api.github.com/markdown', json=payload)
    html = github_markdown_conversion_request.text
    return render_template('career/project.html', html=html, project=project, projects=project_repos)
