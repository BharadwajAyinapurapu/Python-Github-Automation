import click
import time
import github
from github import Github, Organization, Repository, AuthenticatedUser
from vars import *


def main(repo_name, github_org, template_name):

    if github_org != GITHUB_ORG:
        print("ERROR, Github organization is not supported")
        exit(1)
    
    # Read PAT from local
    GITHUB_TOKEN = read_PAT(Path_to_secret)
    
    # Logging in to Github account
    _github, _org, _user = login(GITHUB_URL, GITHUB_TOKEN, github_org)

    # Creating a repository
    repo_descr = repo_name                                  
    template_repo = _org.get_repo(template_name)
    new_repo = create_new_repo(repo_name, repo_descr, template_repo, _org)
    
    # Repository settings
    set_repo_settings(new_repo)

    # Adding collaborators
    collaborators = collaborator_list
    add_collaborators(new_repo, _github, collaborators)

def read_PAT(Path_to_secret: str) -> str:
    with open(Path_to_secret, "r") as f:
        GITHUB_TOKEN = f.readline()
    print(GITHUB_TOKEN)
    print(type(GITHUB_TOKEN))
    return GITHUB_TOKEN


def add_collaborators(new_repo: Repository.Repository, github: Github, collaborators: list[str]) -> None:
    for user in collaborators:
        u = github.get_user(user)
        new_repo.add_to_collaborators(collaborator=u, permission="push")
    print("Collaborators added successfully")


def set_repo_settings(repo: Repository.Repository) -> None:
    repo.edit(
        allow_merge_commit=False,
        allow_rebase_merge=True,
        allow_squash_merge=False,
        delete_branch_on_merge=True
    )
    print("Repository options are set now")
    try:
        main_branch = repo.get_branch("main")
        main_branch.edit_protection(
            enforce_admins=True,
            dismiss_stale_reviews=True,
            required_approving_review_count=1
        )
        print("Branch protection rules are set now")
    except github.GithubException as e:
        print(e.data["message"])


def create_new_repo(
    repo_name: str,
    repo_descr: str,
    template_repo: Repository.Repository,
    _org: Organization.Organization
) -> Repository.Repository:
    try:
        _new_repo = _org.create_repo_from_template(
            name=repo_name, description=repo_descr, private=False, repo=template_repo
        )
        print("CREATED the repo %s" % _new_repo)
    except github.GithubException as e:
        if e.status == 422:
            print("Repository %s already exists" % repo_name)
            _new_repo = _org.get_repo(repo_name)
        else:
            print(e.data["message"])
            exit(1)

    time.sleep(5)
    print(list(_new_repo.get_branches()))
    return _new_repo

def login(url: str, token: str, github_org: str) -> tuple[Github, Organization.Organization, AuthenticatedUser.AuthenticatedUser]:
    _g = Github(login_or_token=token)
    _user = _g.get_user()
    print(_user)
    login = _user.login
    print(login)
    _org = _g.get_organization(github_org)
    print(list(_org.get_repos()))
    return _g, _org, _user

if __name__ == "__main__":
    main(repo_name, github_org, template_name)