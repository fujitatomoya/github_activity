import argparse
import datetime
import requests
import string

from string import Template
from typing import (
    List,
    Optional,
)


class BlankFormatter(string.Formatter):
    def __init__(self, default=''):
        self.default=default

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default)
        else:
            return string.Formatter.get_value(key, args, kwds)


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


def query_contribution(
    token: str, query: str
):
    contribution = [] # result based on single query
    cursor = 'null'
    has_next_page = True

    while has_next_page:
        contribution_query = CONTRIBUTION_QUERY.substitute(
            search_query=query,
            cursor=cursor)
        try:
            results = graphql_query(contribution_query, token)['data']
        except Exception as error:
            print("Failed to call graphql_query:", type(error).__name__, error)
        cursor = results['search']['pageInfo']['endCursor']
        has_next_page = results['search']['pageInfo']['hasNextPage']
        contribution += results['search']['edges']

    return contribution


def query_contributions(
    token: str, accounts: List[str], orgs: List[str], since: datetime.date
):
    contributions = [] # result via all queries

    # is:pr is:merged mentions:fujitatomoya merged:>=2020-12-21
    search_query = ' '.join([
        'sort:updated-desc',
        'is:pr is:merged',
        ' '.join(['mentions:{}'.format(a) for a in accounts]),
        ' '.join(['org:{}'.format(o) for o in orgs]),
        'merged:>={}'.format(since.isoformat())
    ])
    contributions += query_contribution(token, search_query)

    # is:pr is:merged author:fujitatomoya merged:>=2020-12-21
    search_query = ' '.join([
        'sort:updated-desc',
        'is:pr is:merged',
        ' '.join(['author:{}'.format(a) for a in accounts]),
        ' '.join(['org:{}'.format(o) for o in orgs]),
        'merged:>={}'.format(since.isoformat())
    ])
    contributions += query_contribution(token, search_query)

    return contributions


def format_github_time_to_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').date().isoformat()


def format_contribution(node: dict):
    # author:name could be null, that leads KeyError
    if len(node['author']) != 0:
        author_name = node['author']['name']
    else:
        author_name = 'Not registered'
    return '"{}" | {} | {} (merged {})'.format(
        node['title'],
        author_name,
        node['permalink'],
        format_github_time_to_date(node['mergedAt']))


def print_report(
    contributions: List[dict], since: datetime.date, accounts: List[str], orgs: List[str]
):
    print('# Contributions')
    print('By Authors: {}'.format(', '.join(accounts)))
    print('To Repositories in Organizations: {}'.format(', '.join(orgs)))
    print('Merged Since: {}'.format(since.isoformat()))
    print('This report generated: {}'.format(datetime.date.today().isoformat()))
    byrepo = {}
    for c in contributions:
        node = c['node']
        repo = node['repository']['nameWithOwner']
        if byrepo.get(repo) is None:
            byrepo.setdefault(repo, []).append(format_contribution(node))
        elif (format_contribution(node) not in byrepo.get(repo)):
            # get rid of redundant string.
            byrepo.setdefault(repo, []).append(format_contribution(node))
        else:
            pass

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
        '-a', '--accounts',
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
        parsed.token, parsed.accounts, parsed.orgs, parsed.since)
    print_report(contributions, parsed.since, parsed.accounts, parsed.orgs)


if __name__ == '__main__':
    main()