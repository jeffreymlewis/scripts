#!/usr/bin/env python3

"""Find a CCI pipeline by commit, and wait for it to terminate.

Find the CircleCI pipeline & workflow(s) for a given git commit, wait for it
to finish, and exit with appropriate return code and status message. Also emit
the CCI Pipeline URL as a convenience for the end user.

Usage:
    check_workflow_status.py [options] --branch=VCS_BRANCH --commit=VCS_COMMIT
    check_workflow_status.py --help

Options:
    --vcs=VCS       Version Control System (github|bitbucket) [default: github]
    --org=ORG       VCS organization [default: jeffreymlewis]
    --project=PROJECT  Project in the VCS org [default: scripts]
    -h, --help      Show this screen
"""

import os
import time
import sys

import docopt    # pylint: disable=import-error
import requests  # pylint: disable=import-error

# CircleCI API endpoint
CIRCLE_API_ENDPOINT = 'https://circleci.com/api/v2'

# All possble CCI status messages.
# https://circleci.com/docs/api/v2/#operation/listWorkflowsByPipelineId
CIRCLE_FAILURE_STATUS = {'failed', 'error', 'failing', 'canceled',
                         'unauthorized'}
CIRCLE_SUCCESS_STATUS = {'success', 'not_run'}
CIRCLE_WAITING_STATUS = {'running', 'on_hold'}


def _find_commit_in_cci_pipeline_object(response: dict,
                                        commit_ref: str) -> dict:
    """Find a specific commit in a CCI '/pipeline' API response object.
    https://circleci.com/docs/api/v2/#operation/listPipelines"""
    for item in response['items']:
        if item['vcs']['revision'] == commit_ref:
            return item
    return None


def _get_pipeline_from_commit(project_slug: str, branch: str,
                             commit_ref: str) -> dict:
    """Loop though all the CircleCI pipelines for a given project/branch, returning
    the id & number of the CircleCI pipeline matching a specific commit. There
    should be only one pipeline per git commit."""

    url = f'{CIRCLE_API_ENDPOINT}/project/{project_slug}/pipeline'
    query_string = {'branch': branch}
    headers = {'Circle-Token': os.environ['CIRCLE_API_TOKEN']}

    next_page_token = "first_loop"
    while next_page_token:
        if next_page_token and next_page_token != "first_loop":
            query_string['page-token'] = next_page_token

        # Make an API call
        response = requests.get(url, headers=headers, params=query_string)
        json_response = response.json()

        # If the 'items' key exists, we know the API call was successful
        if 'items' in json_response.keys():
            next_page_token = json_response['next_page_token']
            pipeline_metadata = _find_commit_in_cci_pipeline_object(
                json_response, commit_ref)
            if pipeline_metadata:
                return pipeline_metadata
        # If the 'items' key doesn't exist, there was an error in the API call
        else:
            sys.exit(f'ERROR: CircleCI says: {json_response}')
        # time.sleep(1) # don't get throttled by the CCI API server


def _get_pipeline_workflows(pipeline_id: str) -> dict:
    """Get all workflows in a CCI pipeline"""
    url = f'{CIRCLE_API_ENDPOINT}/pipeline/{pipeline_id}/workflow'
    headers = {'Circle-Token': os.environ['CIRCLE_API_TOKEN']}

    # Make an API call
    response = requests.get(url, headers=headers)
    return response.json()


def main(args):
    """Find pipeline, find workflow(s), check workflow status, exit with
    appropriate status & message."""

    branch = args['--branch']
    commit = args['--commit']
    vcs = args['--vcs']
    org = args['--org']
    project = args['--project']

    # The "project_slug" in part of the API's URL. (This is a CCI term.)
    project_slug = f'{vcs}/{org}/{project}'

    # Find the CCI pipeline for this commit
    pipeline = _get_pipeline_from_commit(
        project_slug=project_slug,
        branch=branch,
        commit_ref=commit,
    )
    if not pipeline:
        sys.exit(f'ERROR: Could not find commit {commit} in project '
                 f'{project_slug} on branch {branch}')

    # Emit the direct URL to this pipeline, for the manual approval step.
    pipeline_number = pipeline['number']
    pipeline_url = f'https://app.circleci.com/pipelines/{vcs}/{org}/{project}/{pipeline_number}'
    print(f'Waiting for "{project}" pipeline to complete.\n\n'
          f'{pipeline_url}\n\n')

    # Wait for all workflows in the pipeline to complete. We use set
    # intersection to check status against known CCI status messages.
    status = ["running"]
    while CIRCLE_WAITING_STATUS & set(status):
        workflows = _get_pipeline_workflows(pipeline['id'])
        status = [item['status'] for item in workflows['items']]
        time.sleep(1)  # avoid CCI throttling

    # Now that all workflows are complete, check for failures
    if CIRCLE_FAILURE_STATUS & set(status):
        failed_workflow_ids = [item['id'] for item in workflows['items']
                               if item['status'] in CIRCLE_FAILURE_STATUS]
        sys.exit(f'The following workflows failed: {failed_workflow_ids}')


if __name__ == '__main__':
    if not 'CIRCLE_API_TOKEN' in os.environ:
        sys.exit('Please set environment variable CIRCLE_API_TOKEN')
    main(docopt.docopt(__doc__))
