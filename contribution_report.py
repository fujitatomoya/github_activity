import argparse
import datetime
import requests

from string import Template
from typing import (
    List,
    Optional,
)


CONTRIBUTION_QUERY = Template("""
{
  search(query: "$search_query", type: ISSUE, last: 100, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        ... on PullRequest {
          author {
            ... on User {
              name
            }
          }
          createdAt
          permalink
          repository {
            nameWithOwner
          }
          title
          updatedAt
          mergedAt
        }
      }
    }
  }
}
""")


def graphql_query(query: str, token: Optional[str] = None):
    headers = {'Authorization': 'Bearer {}'.format(token)} if token else None
    request = requests.post(
        'https://api.github.com/graphql',
        json={'query': query},
        headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise RuntimeError('Query failed with code {}'.format(request.status_code))


def query_contributions(
    token: str, authors: List[str], orgs: List[str], since: datetime.date
):
    search_query = ' '.join([
        'sort:updated-desc',
        'is:pr is:merged',
        ' '.join(['author:{}'.format(a) for a in authors]),
        ' '.join(['org:{}'.format(o) for o in orgs]),
        'merged:>={}'.format(since.isoformat())
    ])

    cursor = 'null'
    has_next_page = True
    contributions = []
    while has_next_page:
        contribution_query = CONTRIBUTION_QUERY.substitute(
            search_query=search_query,
            cursor=cursor)
        results = graphql_query(contribution_query, token)['data']
        cursor = results['search']['pageInfo']['endCursor']
        has_next_page = results['search']['pageInfo']['hasNextPage']
        contributions += results['search']['edges']
    return contributions


def format_github_time_to_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').date().isoformat()


def format_contribution(node: dict):
    return '"{}" | {} | {} (merged {})'.format(
        node['title'],
        node['author']['name'],
        node['permalink'],
        format_github_time_to_date(node['mergedAt']))


def print_report(
    contributions: List[dict], since: datetime.date, authors: List[str], orgs: List[str]
):
    print('# Contributions')
    print('By Authors: {}'.format(', '.join(authors)))
    print('To Repositories in Organizations: {}'.format(', '.join(orgs)))
    print('Merged Since: {}'.format(since.isoformat()))
    print('This report generated: {}'.format(datetime.date.today().isoformat()))
    print('Contribution count (remember to update if you remove things): {}'.format(
        len(contributions)))
    byrepo = {}
    for c in contributions:
        node = c['node']
        repo = node['repository']['nameWithOwner']
        byrepo.setdefault(repo, []).append(format_contribution(node))

    for repo, contribs in sorted(byrepo.items()):
        print('* {}'.format(repo))
        for c in contribs:
            print('  * {}'.format(c))


def IsoDate(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--since',
        type=IsoDate,
        default=datetime.date.today() - datetime.timedelta(days=30),
        help='Report contributions merged on or after this date '
             '(format YYYY-MM-DD). Defaults to 30 days ago')
    parser.add_argument(
        '-t', '--token',
        required=True,
        help='Github access token to access github.com')
    parser.add_argument(
        '-a', '--authors',
        nargs='+',
        required=True,
        help='Report contributions for these github usernames')
    parser.add_argument(
        '-o', '--orgs',
        nargs='+',
        required=True,
        help='Report contributions only to repos these github organizations')
    if args is None:
        parsed = parser.parse_args()
    else:
        parsed = parser.parse_args(args)

    contributions = query_contributions(
        parsed.token, parsed.authors, parsed.orgs, parsed.since)
    print_report(contributions, parsed.since, parsed.authors, parsed.orgs)


if __name__ == '__main__':
    main()