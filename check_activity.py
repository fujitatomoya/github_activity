from github import Github
import networkx as nx
import pygraphml as pg

# Replace this to your own GitHub API key
TOKEN = '27049d05cdb285d10fbe37c1229f55c6a49c958b'

######## static definitions ##########
# Edge Types (interaction)
COMMIT_TO = 'commit_to'
OWNER_OF = 'owner_of'

# Node Types
USER = 'user'
REPO = 'repo'
SEED = 'seed'
SEED_COMMITTER = 'seed_committer'

# threshold if the repository is displayed as in result.
# expecting 100 stars are good enough to check the repository.
STAR_TH = 100

# Seeds for Graphical Result
SEEDS = [
    'ros2/design',
    'ros2/rclcpp'

]

client = Github(TOKEN)

# NetworkX Object
g = nx.MultiDiGraph(name='Github Activity')

# Extract committers of the project
def extract_committers(repo, repo_node, expand_user_repos, user_type):
    committers = repo.get_contributors()
    for committer in committers:
        login = committer.login
        g.add_node(login, type = user_type)
        extract_user_info(g, login, committer)
        
        g.add_edge(login, repo_node, interaction = COMMIT_TO)
       
        if expand_user_repos:
            committer_repos = committer.get_repos()
            add_user_repos(login, committer_repos)
        

# Filter major projects
def add_user_repos(user, repos):
    for repo in repos:
        # Pick only highly starred projects
        stargazers = repo.stargazers_count
        if stargazers < STAR_TH:
            continue
                
        repo_name = repo.full_name
        if g.has_node(repo_name) == False:
            g.add_node(repo_name, type=REPO)
            extract_repo_info(g, repo_name, repo)

        g.add_edge(user, repo_name,  interaction = OWNER_OF)
        extract_committers(repo, repo_name, False, USER)


# Extract user information
def extract_user_info(graph, user_id, user):
    node = graph.node[user_id]
    name = user.name
    if name is None:
        name = user_id
    
    node['login'] = user_id 
    node['name'] = name
    node['followers'] = user.followers
    node['location'] = user.location
    node['bio'] = user.bio
    node['score'] = node['followers']
    
# Extract repository information
def extract_repo_info(graph, repo_id, repo):
    node = graph.node[repo_id]
    
    node['name'] = repo.name
    node['description'] = repo.description
    node['homepage'] = repo.homepage
    node['stargazers'] = repo.stargazers_count
    node['watchers'] = repo.watchers_count
    node['fork_count'] = repo.forks_count
    node['score'] = node['watchers'] + node['stargazers']
    node['language'] = repo.language

for seed in SEEDS:
    repo = client.get_repo(seed)
    repo_name = repo.full_name
    #print(repo_name)
    g.add_node(repo_name, type=SEED)
    extract_repo_info(g, repo_name, repo)
    extract_committers(repo, repo_name, True, SEED_COMMITTER)

#print(g.number_of_nodes())
#print(g.number_of_edges())

# Replace None to empty string
nodes = g.nodes()
for node_id in nodes:
    node = g.node[node_id]
    keys = node.keys()
    for key in keys:
        if node[key] is None:
            node[key] = ''

nx.write_graphml(g, 'github_avtivity.graphml')

#parser = pg.GraphMLParser()
#gshow = parser.parse("github_avtivity.graphml")
#gshow.show()

