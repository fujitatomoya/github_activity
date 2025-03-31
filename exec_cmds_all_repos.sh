#!/bin/bash

# Note: trap cannot handle return code bu signals only. this only works with general error signal.
function exit_trap() {
    # shellcheck disable=SC2317  # Don't warn about unreachable commands in this function
    if [ $? != 0 ]; then
        echo "Command [$BASH_COMMAND] is failed"
        exit 1
    fi
}

# This function is defined by user requirement, what needs to be done in each repo.
function user_operation_base () {
    trap exit_trap ERR
    echo "[${FUNCNAME[0]}]: Executing user defined operation."
    if [ -f ".github/ISSUE_TEMPLATE.md" ]; then
        echo "Found .github/ISSUE_TEMPLATE.md. Removing it..."
        rm .github/ISSUE_TEMPLATE.md

        echo "Creating new branch 'remove-old-issue-template'..."
        git checkout -b remove-old-issue-template

        echo "Adding changes and committing..."
        git add .github/ISSUE_TEMPLATE.md
        git commit -m "remove .github/ISSUE_TEMPLATE.md (old version of templates)"

        echo "Pushing branch to origin..."
        git push -u origin remove-old-issue-template
    else
        echo ".github/ISSUE_TEMPLATE.md not found. Skipping."
    fi
}

# This function is defined by user requirement, what needs to be done in each repo.
function user_operation_adjust () {
    trap exit_trap ERR
    echo "[${FUNCNAME[0]}]: Executing user defined operation."
    echo "Checkout development branch 'remove-old-issue-template'..."
    git checkout -b remove-old-issue-template origin/remove-old-issue-template
    echo "Adding signoff changes and committing..."
    git commit --signoff --amend -m "remove .github/ISSUE_TEMPLATE.md (old version of templates)"
    echo "Pushing branch to origin..."
    git push --force-with-lease origin remove-old-issue-template
}

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <repo_list_file>"
    exit 1
fi

REPO_LIST=$(realpath "$1")

if [ ! -f "$REPO_LIST" ]; then
    echo "Error: File '$REPO_LIST' not found!"
    exit 1
fi

# Create a directory to store cloned repositories
WORKDIR=$(pwd)/cloned_repos
mkdir -p "$WORKDIR"
cd "$WORKDIR" || exit 1

# Clone each repository
while IFS= read -r repo; do
    if [[ -z "$repo" || "$repo" =~ ^# ]]; then
        continue
    fi
    REPO_URL="git@github.com:$repo.git"
    REPO_NAME=$(basename "$repo")
    
    if [ -d "$REPO_NAME" ]; then
        echo "Repository '$repo' already cloned. Skipping."
    else
        echo "Cloning $repo..."
        git clone "$REPO_URL"
    fi

done < "$REPO_LIST"

# Run git status on each repository
for dir in */; do
    if [ -d "$dir/.git" ]; then
        echo "Checking status of $dir"
        cd "$dir" || continue
        #user_operation_base
        user_operation_adjust
        cd ..
    fi
done

exit 0
