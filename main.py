import requests
import os
import csv

from dotenv import load_dotenv

load_dotenv()

from datetime import date, datetime

date_format = "%Y/%m/%d"

today = datetime.__format__(date.today(), date_format)

arquivo_csv = open('dados.csv', 'w')

escritor = csv.writer(arquivo_csv)

# Configuração do token de acesso pessoal
token = os.getenv("GITHUB_TOKEN")

# Função para obter os repositórios mais populares com a palavra-chave "microservices"
def get_popular_repos_by_keyword(keyword, num_repos):
    url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc&per_page={num_repos}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        raise Exception(f"Failed to fetch repositories: {response.status_code}")

# Função para obter detalhes de um repositório
def get_repo_details(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch repository details: {response.status_code}")

# Função para obter o número de pull requests com paginação
def get_pull_requests(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all"
    headers = {"Authorization": f"token {token}"}
    page = 1
    pull_requests = []
    while True:
        response = requests.get(f"{url}&page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_pull_requests = response.json()
            if not page_pull_requests:
                break
            pull_requests.extend(page_pull_requests)
            page += 1
        else:
            raise Exception(f"Failed to fetch pull requests: {response.status_code}")
    return len(pull_requests)

# Função para obter o número de releases com paginação
def get_releases(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {"Authorization": f"token {token}"}
    page = 1
    releases = []
    while True:
        response = requests.get(f"{url}?page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_releases = response.json()
            if not page_releases:
                break
            releases.extend(page_releases)
            page += 1
        else:
            raise Exception(f"Failed to fetch releases: {response.status_code}")
    return len(releases)

# Função para obter o número de issues fechadas com paginação
def get_closed_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=closed"
    headers = {"Authorization": f"token {token}"}
    page = 1
    closed_issues = []
    while True:
        response = requests.get(f"{url}&page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_closed_issues = response.json()
            if not page_closed_issues:
                break
            closed_issues.extend(page_closed_issues)
            page += 1
        else:
            raise Exception(f"Failed to fetch closed issues: {response.status_code}")
    return len(closed_issues)

# Função para obter a quantidade total de issues
def get_issues_count(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"
    headers = {"Authorization": f"token {token}"}
    page = 1
    issues = []
    while True:
        response = requests.get(f"{url}&page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_issues = response.json()
            if not page_issues:
                break
            issues.extend(page_issues)
            page += 1
        else:
            raise Exception(f"Failed to fetch issues: {response.status_code}")
    return len(issues)

# Função para obter o número de pull requests aceitas
def get_merged_pull_requests_count(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed"
    headers = {"Authorization": f"token {token}"}
    page = 1
    pull_requests = []
    while True:
        response = requests.get(f"{url}&page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_pull_requests = response.json()
            if not page_pull_requests:
                break
            merged_pull_requests = filter(lambda x: x["merged_at"] != "null", page_pull_requests)
            pull_requests.extend(merged_pull_requests)
            page += 1
        else:
            raise Exception(f"Failed to fetch merged pull requests: {response.status_code}")
    return len(pull_requests)

# Função para coletar e imprimir informações dos repositórios
def collect_and_print_repo_info(repos):
    for repo in repos:
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        repo_details = get_repo_details(owner, repo_name)
        
        pull_requests = get_pull_requests(owner, repo_name)
        releases = get_releases(owner, repo_name)
        closed_issues = get_closed_issues(owner, repo_name)

        print(f"Repository: {repo_name}")
        print(f"Owner: {owner}")
        print(f"URL: {repo_details['html_url']}")
        print(f"Stars: {repo_details['stargazers_count']}")
        print(f"Forks: {repo_details['forks_count']}")
        print(f"Commits: {repo_details['open_issues_count']}")
        print(f"Watchers: {repo_details['watchers_count']}")
        print(f"Pull Requests: {pull_requests if pull_requests is not None else 'N/A'}")
        print(f"Last Commit Date: {repo_details['pushed_at']}")
        print(f"Main Language: {repo_details['language']}")
        print(f"License: {repo_details['license']['name'] if repo_details['license'] else 'No license'}")
        print(f"Contributors: {repo_details['network_count']}")
        print(f"Size: {repo_details['size']} KB")
        print(f"Main Branch: {repo_details['default_branch']}")
        print(f"Releases: {releases if releases is not None else 'N/A'}")
        print(f"Closed Issues: {closed_issues if closed_issues is not None else 'N/A'}")
        print(f"Topics: {', '.join(repo_details['topics']) if 'topics' in repo_details else 'No topics'}")
        print("-" * 200)

# Função para imprimir dados dos repositórios
def print_repo_data(repos):
    escritor.writerow(["Repositório", "Idade", "PR's aceitas", "Total de releases", "Dias desde última atualização", "Linguagem principal", "Percentual de issues fechadas"])
    for repo in repos:
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        repo_details = get_repo_details(owner, repo_name)
        releases = get_releases(owner, repo_name)
        closed_issues = get_closed_issues(owner, repo_name)
        issues_count = get_issues_count(owner, repo_name)
        merged_pull_requests = get_merged_pull_requests_count(owner, repo_name)
        treated_closed_issues = closed_issues if closed_issues is not None else 0
        treated_issues_count = issues_count if issues_count is not None else 0
        treated_releases = releases if releases is not None else 'N/A'

        format_string = "%Y-%m-%dT%H:%M:%SZ"
        creation_date = datetime.strptime(repo_details['created_at'], format_string)
        age = datetime.strptime(today, date_format) - creation_date
        last_update_date = datetime.strptime(repo_details['pushed_at'], format_string)
        days_since_updated = datetime.strptime(today, date_format) - last_update_date

        repositorio = f"https://github.com/{owner}/{repo_name}"
        percentual_issues = "{:10.2f}".format(0 if treated_issues_count == 0 else treated_closed_issues/treated_issues_count)

        escritor.writerow([repositorio, age.days, merged_pull_requests, treated_releases, days_since_updated.days, repo_details['language'], percentual_issues])

# Main
if __name__ == "__main__":
    keyword = "microservices"
    num_repos = 10  # Número de repositórios a serem coletados
    try:
        popular_repos = get_popular_repos_by_keyword(keyword, num_repos)
        # collect_and_print_repo_info(popular_repos)
        print_repo_data(popular_repos)
        arquivo_csv.close()
    except Exception as e:
        print("ERROR: ",e)
