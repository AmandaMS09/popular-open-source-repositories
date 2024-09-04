import requests
import os
import csv

from dotenv import load_dotenv

load_dotenv()

from datetime import date, datetime

today = date.today()

arquivo_csv = open('dados.csv', 'w')

escritor = csv.writer(arquivo_csv)

# Configuração do token de acesso pessoal
token = os.getenv("GITHUB_TOKEN")

graphQLEndpoint = "https://api.github.com/graphql"

query = """query($after: String) {
  search(type: REPOSITORY, query: "stars:>1600", first: 25, after: $after) {
    pageInfo {
      endCursor
    }
    edges {
      node {
        ... on Repository {
          url
          createdAt
          pushedAt
          primaryLanguage {
            name
          }
          issues {
            totalCount
          }
          closedIssues: issues(states: CLOSED) {
            totalCount
          }
          pullRequests(states: MERGED) {
            totalCount
          }
          releases {
            totalCount
          }
          stargazers {
            totalCount
          }
        }
      }
    }
  }
}"""

# Função para executar a consulta GraphQL
def run_query(query, variables):
    request = requests.post(graphQLEndpoint, json={'query': query, 'variables': variables}, headers={"Authorization": f"Bearer {token}"})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"FAILED TO RUN QUERY. Status code: {request.status_code}")

# Função para imprimir dados dos repositórios
def print_repo_data(repos):
    for repo in repos:
        repo = repo['node']
        
        format_string = "%Y-%m-%dT%H:%M:%SZ"
        creation_date = datetime.strptime(repo['createdAt'], format_string)
        created_at = datetime.date(creation_date)
        age = today - created_at

        merged_pull_requests = repo['pullRequests']['totalCount']

        releases = repo['releases']['totalCount']

        last_update_date = datetime.strptime(repo['pushedAt'], format_string)
        last_updated = datetime.date(last_update_date)
        days_since_updated = today - last_updated

        primary_language = repo['primaryLanguage']['name'] if repo['primaryLanguage'] is not None else "N/A"

        closed_issues = repo['closedIssues']['totalCount']
        issues_count = repo['issues']['totalCount']
        percentual_issues = "{:.2%}".format(0 if issues_count == 0 else closed_issues/issues_count)

        escritor.writerow([repo['url'], age.days, merged_pull_requests, releases, days_since_updated.days, primary_language, issues_count, percentual_issues])

# Main
if __name__ == "__main__":
    try:
        escritor.writerow(["Repositório", "Idade (dias)", "PR's aceitas", "Releases", "Última atualização (dias)", "Linguagem principal", "Issues", "Issues fechadas"])
        variables = {"after": None}
        for i in range(40):
            res = run_query(query, variables)
            print_repo_data(res['data']['search']['edges'])
            variables = {"after": res['data']['search']['pageInfo']['endCursor']}
        arquivo_csv.close()
    except Exception as e:
        print("ERROR: ",e)
